"""Firmware update entity for a CH592 device.

This exposes the WCH backup-OTA upload as a native Home Assistant update entity:
the version card shows up in Settings -> Updates and on the device page, with an
install button and a progress bar.
"""

from __future__ import annotations

import logging

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_FIRMWARE
from .coordinator import Ch592OtaCoordinator
from .entity import build_device_info
from .firmware import (
    is_newer,
    manifest_version,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: Ch592OtaCoordinator = entry.runtime_data
    async_add_entities([Ch592FirmwareUpdateEntity(coordinator)])


class Ch592FirmwareUpdateEntity(UpdateEntity):
    """Firmware update backed by the bundled .bin and its .json sidecar."""

    _attr_has_entity_name = True
    _attr_translation_key = "firmware"
    _attr_should_poll = False
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = (
        UpdateEntityFeature.INSTALL | UpdateEntityFeature.PROGRESS
    )

    def __init__(self, coordinator: Ch592OtaCoordinator) -> None:
        self.coordinator = coordinator
        self._address = coordinator.address
        self._attr_unique_id = f"{self._address}_firmware_update"
        self._latest_version: str | None = None
        self._latest_meta: dict[str, object] = {}
        self.cloud = coordinator.cloud
        self._preparing = False

    # ------------------------------------------------------------ lifecycle

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )
        if self.cloud is not None:
            self.async_on_remove(self.cloud.async_add_listener(self._handle_cloud_update))
        await self._async_load_latest()

    # --------------------------------------------------------------- update API

    @property
    def device_info(self):
        return build_device_info(self.coordinator)

    @property
    def available(self) -> bool:
        return True

    @property
    def in_progress(self) -> bool:
        """Keep background progress independent of HA's service wrapper."""
        return self._preparing or self.coordinator.data.get("status") in (
            "starting", "running", "rebooting"
        )

    @property
    def update_percentage(self) -> float | None:
        if self._preparing:
            return 0
        if self.in_progress:
            return min(max(float(self.coordinator.data.get("progress", 0)), 0), 99)
        return None

    @property
    def installed_version(self) -> str | None:
        value = self.coordinator.data.get("firmware_version")
        return str(value) if value else None

    @property
    def latest_version(self) -> str | None:
        """Never offer a downgrade: a stale local .bin must not look newer."""
        installed = self.installed_version
        manifest = self._cloud_manifest()
        if manifest is not None:
            cloud_version = manifest_version(manifest)
            return cloud_version if is_newer(cloud_version, installed) else installed
        if self._latest_version and is_newer(self._latest_version, installed):
            return self._latest_version
        return installed

    @property
    def release_summary(self) -> str | None:
        manifest = self._cloud_manifest() or {}
        notes = manifest.get("notes")
        size = manifest.get("size") or self._latest_meta.get("size")
        crc = manifest.get("crc32") or self._latest_meta.get("crc32")
        parts = []
        if notes:
            parts.append(str(notes))
        if size:
            parts.append(f"{int(size) // 1024} KiB")
        if crc:
            parts.append(f"CRC {crc}")
        parts.append("固件 1.4.7 起点击更新后自动开启 OTA；旧版首次升级仍需长按 B 约 10 秒")
        return " · ".join(parts)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        manifest = self._cloud_manifest() or {}
        error = (
            getattr(self.cloud, "last_exception", None)
            if self.cloud and not getattr(self.cloud, "last_update_success", True)
            else None
        )
        return {
            "manifest_url": getattr(self.cloud, "url", None),
            "upstream_version": manifest_version(manifest),
            "firmware_notes": manifest.get("notes"),
            "firmware_built": manifest.get("built"),
            "manifest_error": str(error) if error else None,
            "firmware_ready": bool(manifest and self.cloud and self.cloud.is_prepared(manifest)),
            "download_error": getattr(self.cloud, "prefetch_error", None),
            "download_path": str(getattr(self.cloud, "_prepared_path", "") or "") or None,
            "ota_status": "preparing" if self._preparing else self.coordinator.data.get("status"),
            "ota_phase": "downloading" if self._preparing else self.coordinator.data.get("phase"),
            "ota_error": None if self._preparing else self.coordinator.data.get("error"),
            "ota_message": self.coordinator.data.get("auto_note"),
            "wake_attempts": self.coordinator.data.get("wake_attempts"),
            "wake_elapsed_s": self.coordinator.data.get("wake_elapsed_s"),
            "wake_last_error": self.coordinator.data.get("wake_last_error"),
        }

    async def async_install(
        self, version: str | None = None, backup: bool = False
    ) -> None:
        """Accept an update; the coordinator owns progress and completion."""
        task = self.coordinator.current_task
        if self._preparing or (task is not None and not task.done()):
            return
        self._preparing = True
        self.async_write_ha_state()
        try:
            manifest = self._cloud_manifest()
            if self.cloud is not None and not manifest and not (
                self.coordinator.entry.options.get(CONF_FIRMWARE)
            ):
                raise HomeAssistantError("无法读取固件清单，请先检查更新；不会改用旧本地固件")
            cloud_version = manifest_version(manifest)
            if manifest and is_newer(cloud_version, self.installed_version):
                try:
                    image = await self.cloud.async_prepare_firmware(manifest)
                except HomeAssistantError as err:
                    self.cloud.prepare_error = str(err)
                    raise
                await self.coordinator.async_start_ota(
                    version=version or cloud_version, image=image, meta=manifest,
                )
            else:
                await self.coordinator.async_start_ota()
        finally:
            self._preparing = False
            self.async_write_ha_state()

        # Do not keep the service request open through the BLE session. A
        # frontend request timeout must not look like a failed firmware update.
        # The existing coordinator task reports every terminal state and error.

    def _cloud_manifest(self) -> dict[str, object] | None:
        if self.cloud is None or not isinstance(self.cloud.data, dict):
            return None
        return self.cloud.data

    # --------------------------------------------------------------- internals

    async def _async_load_latest(self) -> None:
        try:
            path = self.coordinator.resolve_firmware_path()
            image, meta = await self.hass.async_add_executor_job(
                self.coordinator.read_image, path
            )
        except (OSError, HomeAssistantError) as err:
            # The local image is only a fallback for the cloud manifest now, so
            # a missing file is normal unless a path was configured on purpose.
            if self.coordinator.entry.options.get(CONF_FIRMWARE):
                _LOGGER.warning("无法读取固件文件: %s", err)
            else:
                _LOGGER.debug("没有本地固件文件，使用云端清单: %s", err)
            return
        version = meta.get("version")
        if version:
            self._latest_version = str(version)
        else:
            self._latest_version = None
        self._latest_meta = meta
        self.async_write_ha_state()

    @callback
    def _handle_cloud_update(self) -> None:
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
