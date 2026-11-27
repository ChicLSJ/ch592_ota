"""Runtime state and OTA task management for one CH592 device."""

from __future__ import annotations

import asyncio
import json
import logging
import zlib
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_register_callback,
    async_last_service_info,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .ble_ota import (
    Ch592OtaClient,
    OtaError,
    OtaMtuError,
    async_set_gas,
    async_set_threshold,
)
from .bthome import has_bthome_data, parse_bthome_fields, raw_advertisement_fields
from .remote_wake import async_request_remote_ota
from .const import (
    CONF_AUTO_INSTALL,
    CONF_FIRMWARE,
    CONF_VERSION,
    DEFAULT_AUTO_INSTALL,
    DEFAULT_FIRMWARE,
    GAS_MAX_UNITS,
    GAS_SET_PENDING_SECONDS,
    IMAGE_SIZE,
    OTA_SERVICE_UUID,
    REBOOT_TIMEOUT,
    REMOTE_WAKE_WAIT_SECONDS,
    THRESHOLD_MAX,
    THRESHOLD_MIN,
)
from .firmware import (
    FirmwareCloudCoordinator,
    is_newer,
    manifest_version,
)

_LOGGER = logging.getLogger(__name__)

Listener = Callable[[], None]


class Ch592OtaCoordinator:
    """Holds the latest advertisement data and the running OTA task."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.address: str = entry.data["address"]
        self.data: dict[str, object] = {
            "firmware_version": None,
            "ads": 0,
            "last_seen": None,
            "ota_mode": False,
            "status": "idle",
            "phase": "idle",
            "progress": 0,
            "uploaded": 0,
            "total": 0,
            "error": None,
        }
        self._listeners: set[Listener] = set()
        self._unregister_bt = None
        self._task: asyncio.Task | None = None
        self._client: Ch592OtaClient | None = None
        self._requested_chunk: int | None = None
        self.cloud: FirmwareCloudCoordinator | None = None
        self._auto_task: asyncio.Task | None = None
        self._last_diag_notify = 0.0
        self._run_started: float | None = None
        self._reboot_start_seq = 0
        self._ota_ready = asyncio.Event()
        self._remote_ready = asyncio.Event()
        self._last_ota_seen = 0.0
        # Any advertisement from this address: proves a proxy has a fresh path.
        self._adv_seen = asyncio.Event()
        # Set once a normal BTHome advertisement arrives, so a leftover OTA
        # mode from a previous session does not trigger an upgrade by itself.
        self._seen_bthome = False
        # Gas value written over the OTA channel: draft, armed intent, result.
        self.data["gas_value"] = None
        self.data["gas_target"] = None
        self.data["gas_pending"] = None
        self.data["gas_result"] = None
        self._gas_pending_until = 0.0
        self._gas_task: asyncio.Task | None = None
        # Pulse threshold (firmware >= 1.4.1): device value, draft, armed intent.
        self.data["threshold"] = None
        self.data["threshold_target"] = None
        self.data["threshold_pending"] = None
        self.data["threshold_result"] = None
        self._threshold_pending_until = 0.0

    # ------------------------------------------------------------- lifecycle

    async def async_start(self) -> None:
        self._unregister_bt = async_register_callback(
            self.hass,
            self._async_bt_callback,
            {"address": self.address},
            BluetoothScanningMode.ACTIVE,
        )
        if info := async_last_service_info(self.hass, self.address, connectable=False):
            self._async_bt_callback(info, None)

    async def async_stop(self) -> None:
        if self._unregister_bt is not None:
            self._unregister_bt()
            self._unregister_bt = None
        if self._gas_task is not None and not self._gas_task.done():
            self._gas_task.cancel()
            await asyncio.gather(self._gas_task, return_exceptions=True)
        await self.async_abort(quiet=True)

    # -------------------------------------------------------------- listeners

    @callback
    def async_add_listener(self, update_callback: Listener) -> Callable[[], None]:
        self._listeners.add(update_callback)

        @callback
        def remove_listener() -> None:
            self._listeners.discard(update_callback)

        return remove_listener

    @callback
    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    # ------------------------------------------------------------- bluetooth

    @callback
    def _async_bt_callback(
        self,
        service_info: BluetoothServiceInfoBleak,
        change,
    ) -> None:
        # Diagnostics: visible on binary_sensor.*_ota_mode attributes.
        self.data["ads_total"] = int(self.data.get("ads_total", 0)) + 1
        self._adv_seen.set()
        self.data["last_name"] = service_info.name
        self.data["last_uuids"] = list(service_info.service_uuids)[:6]
        self.data["last_data_uuids"] = list(service_info.service_data)[:6]

        # The OTA advertisement is the authoritative signal (it is the only one
        # carrying 0xFEE0) and must be checked before the BTHome parser: HA can
        # report a BTHome payload for the same address, and the cached device
        # name is "GasMeter OTA" in both modes, so the name proves nothing.
        if self._is_ota_advertisement(service_info):
            self._last_ota_seen = asyncio.get_running_loop().time()
            self._ota_ready.set()
            if not self.data["ota_mode"]:
                _LOGGER.info(
                    "检测到 OTA 广播 (uuids=%s data=%s)",
                    list(service_info.service_uuids),
                    list(service_info.service_data),
                )
                self.data["ota_mode"] = True
                self._notify()
                # An armed config write (threshold and/or gas) wins over an
                # automatic upgrade: the user pressed B for that, and a
                # finished upgrade would reboot the device out of OTA mode
                # before the values could be written.
                if (
                    self._gas_pending_value() is not None
                    or self._threshold_pending_value() is not None
                ):
                    self._maybe_apply_pending()
                else:
                    self._maybe_auto_install()
        else:
            fields = parse_bthome_fields(service_info)
            if has_bthome_data(service_info):
                # Phone settings also carries BTHome, but no version object.
                self.data["ota_mode"] = False
                self._ota_ready.clear()
            version = fields.get("version")
            gas = fields.get("gas")
            if gas is not None:
                self.data["gas_value"] = int(gas)  # type: ignore[arg-type]
            if version is not None:
                self._seen_bthome = True
                self.data["firmware_version"] = str(version)
                if is_newer(str(version), "1.4.6"):
                    self._remote_ready.set()
                else:
                    self._remote_ready.clear()
                registry = dr.async_get(self.hass)
                connections = {(dr.CONNECTION_BLUETOOTH, self.address)}
                if hasattr(registry, "async_get_devices"):
                    devices = registry.async_get_devices(connections=connections)
                else:
                    device = registry.async_get_device(connections=connections)
                    devices = [device] if device else []
                for device in devices:
                    if device.sw_version != str(version):
                        registry.async_update_device(device.id, sw_version=str(version))
                self.data["ads"] = int(self.data["ads"]) + 1
                self.data["last_seen"] = datetime.now(UTC)
                self._notify()
            elif gas is not None:
                self._notify()

        # Throttled refresh so the diagnostic attributes stay current.
        now = asyncio.get_running_loop().time()
        if now - self._last_diag_notify >= 5:
            self._last_diag_notify = now
            self._notify()

    @staticmethod
    def _is_ota_advertisement(service_info: BluetoothServiceInfoBleak) -> bool:
        """Recognise the OTA firmware advertisement.

        Neither the name nor the UUID list is reliable on its own: HA caches
        "GasMeter OTA" as the device name, and the proxy keeps reporting
        0xFFE0/0xFEE0 as *service UUIDs* of normal BTHome broadcasts (left over
        from a GATT discovery during an earlier OTA). The BTHome 0xFCD2 service
        data is the trustworthy marker: the OTA firmware never sends it.
        """
        if (fields := raw_advertisement_fields(service_info)) is not None:
            uuids = set()
            for kind, payload in fields:
                if kind in (0x02, 0x03):
                    uuids.update(payload[i:i + 2] for i in range(0, len(payload) - 1, 2))
                elif kind == 0x16 and len(payload) >= 2:
                    uuids.add(payload[:2])
            return b"\xe0\xfe" in uuids and b"\xd2\xfc" not in uuids
        has_ota_uuid = any(
            u.lower() == OTA_SERVICE_UUID for u in service_info.service_uuids
        ) or any(
            u.lower() in (OTA_SERVICE_UUID, "fee0")
            for u in service_info.service_data
        )
        return has_ota_uuid and not has_bthome_data(service_info)

    # ----------------------------------------------------------- gas value

    def _gas_pending_value(self) -> int | None:
        """The armed gas value, or None when nothing is armed / it expired."""
        value = self.data.get("gas_pending")
        if value is None:
            return None
        now = asyncio.get_running_loop().time()
        if now > self._gas_pending_until:
            self.data["gas_pending"] = None
            self.data["gas_result"] = "待写入已超时取消"
            self._notify()
            return None
        return int(value)  # type: ignore[arg-type]

    @callback
    def set_gas_target(self, value_units: int) -> None:
        """Store the draft value; nothing is written to the device here."""
        self.data["gas_target"] = int(value_units)
        self._notify()

    @callback
    def cancel_gas(self) -> None:
        self.data["gas_pending"] = None
        self.data["gas_result"] = "已取消待写入"
        self._gas_pending_until = 0.0
        if self._threshold_pending_value() is None and self._gas_task is not None:
            self._gas_task.cancel()
        self._notify()

    async def async_set_gas(self, value_units: int) -> dict[str, object]:
        """Write now when the device is in OTA mode, otherwise arm it."""
        if not 0 <= value_units < GAS_MAX_UNITS:
            raise HomeAssistantError(
                f"燃气值超出范围：{value_units / 1000:.3f} m³"
            )
        if self._task is not None and not self._task.done():
            raise HomeAssistantError("升级进行中，请等升级完成后再写入燃气值")
        if self._gas_task is not None and not self._gas_task.done():
            raise HomeAssistantError("写入任务正在进行，请完成后再操作")

        self.data["gas_target"] = int(value_units)
        self.data["gas_pending"] = int(value_units)
        self.data["gas_result"] = None
        self._gas_pending_until = (
            asyncio.get_running_loop().time() + GAS_SET_PENDING_SECONDS
        )
        self._notify()
        if self._remote_ready.is_set() or self.data.get("ota_mode"):
            self._maybe_apply_pending()
        return {
            "result": "armed",
            "value": value_units / 1000,
            "note": "正在自动唤醒并写入，无须按 B" if self._remote_ready.is_set()
                    else "旧固件需长按 B 约 10 秒进入写值通道（15 分钟内有效）",
        }

    async def _async_write_gas(self, value_units: int) -> None:
        self.data["gas_result"] = "writing"
        self._notify()
        try:
            await async_set_gas(self.hass, self.address, value_units)
        except Exception as err:  # noqa: BLE001 - surface every failure
            self.data["gas_result"] = f"写入失败: {err}"
            self._notify()
            raise HomeAssistantError(f"写入燃气值失败: {err}") from err
        self.data.update(
            gas_pending=None,
            gas_value=int(value_units),
            gas_result=f"已写入 {value_units / 1000:.3f} m³",
            ota_mode=False,
            auto_note=None,
            wake_last_error=None,
        )
        self._gas_pending_until = 0.0
        self._notify()

    # ------------------------------------------------------- pulse threshold

    def _threshold_pending_value(self) -> int | None:
        """The armed threshold, or None when nothing is armed / it expired."""
        value = self.data.get("threshold_pending")
        if value is None:
            return None
        now = asyncio.get_running_loop().time()
        if now > self._threshold_pending_until:
            self.data["threshold_pending"] = None
            self.data["threshold_result"] = "待写入已超时取消"
            self._notify()
            return None
        return int(value)  # type: ignore[arg-type]

    @callback
    def set_threshold_target(self, value: int) -> None:
        """Store the draft threshold; nothing is written to the device here."""
        self.data["threshold_target"] = int(value)
        self._notify()

    @callback
    def cancel_threshold(self) -> None:
        self.data["threshold_pending"] = None
        self.data["threshold_result"] = "已取消待写入"
        self._threshold_pending_until = 0.0
        if self._gas_pending_value() is None and self._gas_task is not None:
            self._gas_task.cancel()
        self._notify()

    async def async_set_threshold(self, value: int) -> dict[str, object]:
        """Write now when the device is in OTA mode, otherwise arm it."""
        if not THRESHOLD_MIN <= value <= THRESHOLD_MAX:
            raise HomeAssistantError(
                f"阈值超出范围：{value}（{THRESHOLD_MIN}~{THRESHOLD_MAX}）"
            )
        if self._task is not None and not self._task.done():
            raise HomeAssistantError("升级进行中，请等升级完成后再调整阈值")
        if self._gas_task is not None and not self._gas_task.done():
            raise HomeAssistantError("写入任务正在进行，请完成后再操作")

        self.data["threshold_target"] = int(value)
        self.data["threshold_pending"] = int(value)
        self.data["threshold_result"] = None
        self._threshold_pending_until = (
            asyncio.get_running_loop().time() + GAS_SET_PENDING_SECONDS
        )
        self._notify()
        if self._remote_ready.is_set() or self.data.get("ota_mode"):
            self._maybe_apply_pending()
        return {
            "result": "armed",
            "threshold": value,
            "note": "正在自动唤醒并写入，无须按 B" if self._remote_ready.is_set()
                    else "旧固件需长按 B 约 10 秒进入写值通道（15 分钟内有效）",
        }

    async def _async_write_threshold(self, value: int) -> None:
        self.data["threshold_result"] = "writing"
        self._notify()
        try:
            await async_set_threshold(self.hass, self.address, value)
        except Exception as err:  # noqa: BLE001 - surface every failure
            self.data["threshold_result"] = f"写入失败: {err}"
            self._notify()
            raise HomeAssistantError(f"写入阈值失败: {err}") from err
        # The device does not reboot for a threshold write, so OTA mode stays
        # on and a pending gas value can follow on the same session.
        self.data.update(
            threshold_pending=None,
            threshold=int(value),
            threshold_result=f"已写入阈值 {value}",
            auto_note=None,
            wake_last_error=None,
        )
        self._threshold_pending_until = 0.0
        self._notify()

    @callback
    def _maybe_apply_pending(self) -> None:
        """Write the armed threshold and/or gas value once OTA mode appears."""
        if (
            self._gas_pending_value() is None
            and self._threshold_pending_value() is None
        ):
            return
        if self._task is not None and not self._task.done():
            return
        if self._gas_task is not None and not self._gas_task.done():
            return
        self._gas_task = self.hass.async_create_task(
            self._async_auto_write_pending()
        )

    async def _async_auto_write_pending(self) -> None:
        try:
            await self._async_ensure_ota_mode(for_update=False)
            # Threshold first: it does not reboot, so the gas write (which does)
            # can still happen in this OTA session.
            threshold = self._threshold_pending_value()
            if threshold is not None:
                try:
                    await self._async_write_threshold(threshold)
                except Exception:  # noqa: BLE001 - recorded in threshold_result
                    _LOGGER.exception("自动写入阈值失败")
                    self.data["threshold_pending"] = None
                    self._threshold_pending_until = 0.0
            gas = self._gas_pending_value()
            if gas is not None:
                await self._async_write_gas(gas)
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001 - already recorded in the results
            _LOGGER.exception("自动写入配置失败")
            message = f"写入未完成，请重新点击写入：{err}"
            if self.data.get("gas_pending") is not None:
                self.data["gas_result"] = message
            if self.data.get("threshold_pending") is not None:
                self.data["threshold_result"] = message
            self.data["gas_pending"] = None
            self.data["threshold_pending"] = None
            self._gas_pending_until = self._threshold_pending_until = 0.0
            self._notify()
        finally:
            self._gas_task = None

    # ------------------------------------------------------- auto update

    @property
    def auto_install(self) -> bool:
        return bool(
            self.entry.options.get(CONF_AUTO_INSTALL, DEFAULT_AUTO_INSTALL)
        )

    @callback
    def _maybe_auto_install(self) -> None:
        """Start the OTA as soon as the device advertises OTA mode.

        This is what makes "hold B for about 10 s" enough: no button press in HA.
        Every skip reason is recorded in ``auto_note`` so the decision is
        visible on ``binary_sensor.*_ota_mode`` instead of only in the log.
        """
        def skip(reason: str) -> None:
            self.data["auto_note"] = reason
            _LOGGER.info("自动升级未启动: %s", reason)
            self._notify()

        if not self.auto_install:
            return skip("选项 auto_install_on_ota_mode 已关闭")
        if self._gas_task is not None and not self._gas_task.done():
            return skip("正在写入配置，本次不执行固件升级")
        if self._gas_pending_value() is not None:
            return skip("有待写入的燃气值，本次按 B 优先写燃气值；升级请稍后重新长按 B")
        if self._threshold_pending_value() is not None:
            return skip("有待写入的阈值，本次按 B 优先写阈值；升级请稍后重新长按 B")
        if not self._seen_bthome:
            return skip("本次启动还没看到普通广播，可能是上次遗留的 OTA 模式，未自动升级")
        if self._task is not None and not self._task.done():
            return skip("已有升级任务在运行")
        if self._auto_task is not None and not self._auto_task.done():
            return skip("自动升级已在运行")

        manifest = self.cloud.data if self.cloud else None
        if not isinstance(manifest, dict):
            return skip("没有可用的固件清单")
        version = manifest_version(manifest)
        installed = self.data.get("firmware_version")
        installed_str = str(installed) if installed else None
        if not is_newer(version, installed_str):
            return skip(f"没有新固件（设备 {installed_str}，最新 {version}）")
        if self.cloud.prepared_image(manifest) is None:
            return skip("固件尚未下载校验完成，请先检查更新，再重新长按 B 键")

        self.data["auto_note"] = f"开始自动升级到 {version}"
        _LOGGER.info(
            "检测到 OTA 模式且有新固件 %s（当前 %s），自动开始升级",
            version,
            installed_str,
        )
        self._notify()
        self._auto_task = self.hass.async_create_task(
            self._async_auto_install(manifest, version)
        )

    async def _async_auto_install(
        self, manifest: dict[str, object], version: str | None
    ) -> None:
        try:
            image = self.cloud.prepared_image(manifest) if self.cloud else None
            if image is None:
                raise HomeAssistantError("固件尚未下载校验完成，请先检查更新")
            # Connect immediately; the device only waits five idle seconds.
            await self.async_start_ota(version=version, image=image, meta=manifest)
            if task := self.current_task:
                await task
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001 - surface every failure
            _LOGGER.exception("自动升级失败")
            self.data.update(status="failed", phase="failed", error=str(err))
            self._notify()
        finally:
            self._auto_task = None

    @property
    def last_seen(self) -> datetime | None:
        return self.data.get("last_seen")  # type: ignore[return-value]

    @property
    def current_task(self) -> asyncio.Task | None:
        """The running OTA task, so entities can wait for it to finish."""
        return self._task

    # --------------------------------------------------------------- firmware

    def resolve_firmware_path(self, value: str | None = None) -> Path:
        raw = value or self.entry.options.get(CONF_FIRMWARE, DEFAULT_FIRMWARE)
        config_dir = Path(self.hass.config.config_dir).resolve()
        path = Path(raw)
        if not path.is_absolute():
            path = config_dir / path
        path = path.resolve()
        if not path.is_relative_to(config_dir):
            raise HomeAssistantError("固件路径必须位于 Home Assistant 的 config 目录内")
        return path

    async def async_start_ota(
        self,
        firmware: str | None = None,
        version: str | None = None,
        chunk: int | None = None,
        image: bytes | None = None,
        meta: dict[str, object] | None = None,
    ) -> dict[str, object]:
        if self._task is not None and not self._task.done():
            raise HomeAssistantError("已有 OTA 任务正在运行")
        if self._gas_task is not None and not self._gas_task.done():
            raise HomeAssistantError("正在写入配置，请完成后再更新固件")
        if chunk is not None:
            chunk = int(chunk)
            if chunk % 16 or not 16 <= chunk <= 64:
                raise HomeAssistantError("chunk 必须是 16~64 之间、16 的倍数")
        self._requested_chunk = chunk

        if image is None:
            path = self.resolve_firmware_path(firmware)
            try:
                image, meta = await self.hass.async_add_executor_job(
                    self._read_image, path
                )
            except OSError as err:
                raise HomeAssistantError(f"无法读取固件 {path}: {err}") from err
            source = str(path)
        else:
            meta = meta or {}
            source = "云端固件"

        if not image:
            raise HomeAssistantError(f"固件文件为空: {source}")
        if len(image) > IMAGE_SIZE - 16:
            raise HomeAssistantError(
                f"固件过大: {len(image)} 字节，APP 区最多 {IMAGE_SIZE - 16} 字节"
            )
        if len(image) < 4 or (image[0] & 0x7F) != 0x6F:
            raise HomeAssistantError("文件不是有效的 CH592 APP 镜像（首字不是 JAL 指令）")

        actual_crc = f"0x{zlib.crc32(image) & 0xFFFFFFFF:08X}"
        expected_crc = meta.get("crc32")
        if expected_crc and str(expected_crc).upper() != actual_crc.upper():
            raise HomeAssistantError(
                f"固件 CRC32 不匹配: 元数据 {expected_crc}, 实际 {actual_crc}"
            )

        target = version or meta.get(CONF_VERSION) or None
        self._run_started = asyncio.get_running_loop().time()
        self.data.update(
            status="starting",
            phase="starting",
            progress=0,
            uploaded=0,
            total=len(image),
            error=None,
            duration_s=None,
        )
        self._notify()

        self._task = self.hass.async_create_task(
            self._async_run_ota(image, target), name=f"ch592_ota {self.address}"
        )
        return {"status": "started", "version": target, "size": len(image)}

    async def async_abort(self, quiet: bool = False) -> None:
        task = self._task
        if task is not None and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._task = None
        if not quiet:
            self.data["status"] = "aborted"
            self.data["phase"] = "aborted"
            self._notify()

    # ------------------------------------------------------------- OTA runner

    def read_image(self, path: Path) -> tuple[bytes, dict[str, object]]:
        """Read a firmware image and its sidecar metadata (executor-safe)."""
        return self._read_image(path)

    def _read_image(self, path: Path) -> tuple[bytes, dict[str, object]]:
        image = path.read_bytes()
        meta: dict[str, object] = {}
        sidecar = path.with_name(path.name + ".json")
        if sidecar.exists():
            try:
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                _LOGGER.warning("无法解析固件元数据 %s", sidecar)
        if meta.get("size") not in (None, len(image)):
            _LOGGER.warning(
                "固件元数据大小 %s 与实际大小 %s 不一致",
                meta.get("size"),
                len(image),
            )
        return image, meta

    @callback
    def _on_ota_info(self, info: dict[str, object]) -> None:
        """Device INFO response: voltage, protocol and the negotiated chunks."""
        if "image_size" in info:
            self.data["ota_mode"] = True
            self.data["error"] = None
            self.data["auto_note"] = "OTA 通道已连接"
        if info.get("vdd"):
            self.data["vdd"] = info["vdd"]
            self.data["vdd_min"] = info.get("vdd_min") or info["vdd"]
        if info.get("protocol"):
            self.data["protocol"] = info["protocol"]
        if info.get("threshold") is not None:
            self.data["threshold"] = info["threshold"]
        for key in ("chunk", "verify_chunk", "mtu"):
            if info.get(key) is not None:
                self.data[key] = info[key]
        self._notify()

    def _on_progress(
        self, percent: int, phase: str, done: int, total: int
    ) -> None:
        if phase == "rebooting":
            self._reboot_start_seq = int(self.data["ads"])
        if (
            percent == self.data.get("progress")
            and phase == self.data.get("phase")
            and self.data.get("status") == "running"
        ):
            return
        self.data.update(
            status="running",
            phase=phase,
            progress=percent,
            uploaded=done,
            total=total,
        )
        self._notify()

    @staticmethod
    def _is_retryable(err: Exception) -> bool:
        """Link drops are worth a fresh attempt; protocol errors are not."""
        text = str(err).lower()
        return any(
            key in text
            for key in ("断开", "connect", "timeout", "timed out", "超时")
        )

    async def _async_ensure_ota_mode(self, *, for_update: bool = True) -> None:
        """Wake capable firmware for an explicit update or config write."""
        loop = asyncio.get_running_loop()
        if self.data["ota_mode"] and loop.time() - self._last_ota_seen <= 4:
            return
        self._ota_ready.clear()
        if for_update:
            self.data.update(status="running", phase="waiting_ota", progress=0)
        self._notify()
        started = loop.time()
        deadline = started + REMOTE_WAKE_WAIT_SECONDS
        last_error = None
        self.data.update(wake_attempts=0, wake_elapsed_s=0, wake_last_error=None)
        while loop.time() < deadline:
            capable = self._remote_ready.is_set()
            self.data["wake_elapsed_s"] = round(loop.time() - started, 1)
            if capable:
                self.data["wake_attempts"] += 1
            self.data["auto_note"] = (
                ("固件已校验，等待普通广播窗口自动开启 OTA，无须按 B"
                 if for_update else "等待普通广播窗口自动开启写值通道，无须按 B")
                if capable else "旧固件请长按 B 约 10 秒；新版将自动开启 OTA"
            )
            self._notify()
            no_path = False
            self._adv_seen.clear()
            # Pre-arm the central so its radio can connect within 300 ms.
            # OTA detection races the wake request: manual B remains usable.
            wake = asyncio.create_task(
                async_request_remote_ota(self.hass, self.address)
                if capable else self._remote_ready.wait()
            )
            ready = asyncio.create_task(self._ota_ready.wait())
            try:
                done, _ = await asyncio.wait(
                    (wake, ready),
                    timeout=min(75, max(0, deadline - loop.time())),
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if self._ota_ready.is_set():
                    return
                if wake in done:
                    try:
                        wake.result()
                    except Exception as err:  # retry transient proxy/link errors
                        last_error = str(err)
                        self.data["wake_last_error"] = last_error
                        self.data["wake_elapsed_s"] = round(loop.time() - started, 1)
                        # HA dropped the device (no fresh advertisement
                        # within its stale window): no proxy can connect.
                        no_path = any(key in last_error for key in (
                            "No backend", "no scanner", "尚未发现可连接广播"))
                        self._notify()
                        _LOGGER.debug("等待下一次 OTA 唤醒机会: %s", err)
                    else:
                        if capable:
                            # ACK confirms entry was scheduled (reset in 200 ms).
                            # A proxy may suppress the changed advertisement for
                            # this address. Do not spend the five-second OTA
                            # idle window waiting for that callback: connect
                            # promptly and validate OTA INFO before any erase.
                            self.data["auto_note"] = "唤醒已确认，正在连接 OTA 通道"
                            self.data["wake_elapsed_s"] = round(loop.time() - started, 1)
                            self._notify()
                            await asyncio.sleep(0.4)
                            return
            finally:
                for task in (wake, ready):
                    if not task.done():
                        task.cancel()
                await asyncio.gather(wake, ready, return_exceptions=True)
            if no_path:
                # Spinning every 0.2 s cannot help: wait for the next
                # advertisement, which also restores the proxy path.
                self.data["auto_note"] = "蓝牙代理暂未收到设备广播，等待下一个广播窗口"
                self._notify()
                adv = asyncio.create_task(self._adv_seen.wait())
                ready = asyncio.create_task(self._ota_ready.wait())
                try:
                    await asyncio.wait(
                        (adv, ready),
                        timeout=max(0, deadline - loop.time()),
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                finally:
                    for task in (adv, ready):
                        if not task.done():
                            task.cancel()
                    await asyncio.gather(adv, ready, return_exceptions=True)
                if self._ota_ready.is_set():
                    return
                continue
            await asyncio.sleep(0.2)
        if self._remote_ready.is_set():
            raise OtaError(
                "自动开启 OTA 超时，请检查蓝牙代理与设备信号后重试"
                + (f"：{last_error}" if last_error else "")
            )
        raise OtaError("旧固件尚未进入 OTA，请长按 B 约 10 秒完成首次升级")

    async def _async_run_ota(self, image: bytes, target: str | None) -> None:
        try:
            await self._async_ensure_ota_mode()
            # Chunks must be multiples of 16 so the WCH addr16 field stays aligned.
            requested = self._requested_chunk
            chunks: list[int | None] = [requested] if requested else [None]
            for candidate in (64, 32, 16):
                if candidate not in chunks and (
                    requested is None or candidate < requested
                ):
                    chunks.append(candidate)

            uploaded = False
            # Firmware 1.4.4 exits after 5 idle seconds; reconnect promptly.
            # A full 128-byte upload previously took ~35 s; retrying the whole
            # upload is cheaper than giving up.
            for attempt in range(1, 4):
                if attempt > 1:
                    await self._async_ensure_ota_mode()
                for index, chunk in enumerate(chunks):
                    # A slow failed write can exhaust the idle window too.
                    # Re-check entry for chunk fallback as well as link retries.
                    if index:
                        await self._async_ensure_ota_mode()
                    client = Ch592OtaClient(
                        self.hass,
                        self.address,
                        image,
                        self._on_progress,
                        self._on_ota_info,
                    )
                    self._client = client
                    try:
                        await asyncio.wait_for(
                            client.async_run(chunk), timeout=1800
                        )
                        uploaded = True
                        break
                    except OtaMtuError as err:
                        _LOGGER.warning(
                            "OTA 写入失败，尝试更小的分片 (chunk=%s): %s", chunk, err
                        )
                        self.data["error"] = str(err)
                        self._notify()
                        await asyncio.sleep(2)
                    except OtaError as err:
                        self.data["error"] = str(err)
                        self._notify()
                        if (
                            not self._is_retryable(err)
                            or attempt >= 3
                        ):
                            raise
                        _LOGGER.warning(
                            "OTA 第 %s 次中断（%s），准备整体重传", attempt, err
                        )
                        await asyncio.sleep(2)
                        break
                if uploaded:
                    break
            if not uploaded:
                raise RuntimeError(str(self.data.get("error") or "OTA 上传失败"))

            start_seq = self._reboot_start_seq
            self.data.update(status="rebooting", phase="waiting_reboot", progress=98)
            self._notify()

            if await self._async_wait_for_reboot(start_seq, target):
                self.data.update(
                    status="success", phase="done", progress=100, error=None,
                    auto_note=None, wake_last_error=None,
                )
            else:
                last = self.data.get("firmware_version")
                raise RuntimeError(
                    f"固件已上传，但 {REBOOT_TIMEOUT}s 内未看到目标版本 "
                    f"(期望 {target or '任意'}，最后看到 {last or '无'})"
                )
        except asyncio.CancelledError:
            self.data.update(status="aborted", phase="aborted")
            self._notify()
            raise
        except Exception as err:  # noqa: BLE001 - report every failure to the user
            _LOGGER.exception("CH592 OTA 失败")
            message = str(err)
            lowered = message.lower()
            if "connect" in lowered or "未找到可连接" in message:
                message += (
                    "（请检查蓝牙代理后重试，将自动等待下一次唤醒窗口）"
                    if self._remote_ready.is_set()
                    else "（旧固件请重新长按 B 键约 10 秒进入 OTA 后重试）"
                )
            self.data.update(status="failed", phase="failed", error=message)
            self._notify()
        finally:
            if self._run_started is not None:
                self.data["duration_s"] = round(
                    asyncio.get_running_loop().time() - self._run_started, 1
                )
                self._run_started = None
            self._client = None
            self._task = None
            self._notify()

    async def _async_wait_for_reboot(
        self, start_seq: int, target: str | None
    ) -> bool:
        """Wait until the device advertises again after the reboot.

        The baseline is captured immediately before END, so an advertisement
        received during disconnect still counts. A cached version by itself
        cannot confirm a reboot, especially when reinstalling the same version.
        """
        loop = asyncio.get_running_loop()
        deadline = loop.time() + REBOOT_TIMEOUT
        while loop.time() < deadline:
            fresh = int(self.data["ads"]) > start_seq
            if fresh and (target is None or self.data["firmware_version"] == target):
                return True
            await asyncio.sleep(1)
        return False
