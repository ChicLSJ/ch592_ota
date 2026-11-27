"""Request a device connection only for an explicit update or config write."""

from __future__ import annotations

import asyncio
import logging

from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache
from homeassistant.components.bluetooth import async_ble_device_from_address

from .ble_ota import OtaError
from .const import REMOTE_WAKE_CHAR_UUID, REMOTE_WAKE_REQUEST
from .service_cache import discard_mode_services

_LOGGER = logging.getLogger(__name__)


async def async_request_remote_ota(hass, address: str) -> None:
    """Arm a central connection to catch the device's next 300 ms window.

    No scan or connection is started by manifest polling or advertisements.
    Called after an update image is verified, or after an explicit config write.
    """
    discard_mode_services(hass, address)
    device = async_ble_device_from_address(hass, address, connectable=True)
    if device is None:
        raise OtaError("尚未发现可连接广播，等待下一个普通广播窗口")
    client = None
    try:
        # establish_connection overrides connect(timeout=...) with 20 seconds,
        # even when its constructor receives timeout=75. Keep one continuous
        # connection request armed across the meter's minute-long interval.
        # The coordinator already owns retries, cancellation and the deadline.
        client = BleakClientWithServiceCache(device, timeout=75.0)
        await client.connect(timeout=75.0, dangerous_use_bleak_cache=False)
        characteristic = None
        for service in client.services or ():
            for candidate in service.characteristics:
                if candidate.uuid.lower() == REMOTE_WAKE_CHAR_UUID:
                    characteristic = candidate
                    break
        if characteristic is None:
            # An ESPHome proxy can retain the previous OTA/phone GATT table.
            await client.clear_cache()
            raise OtaError("已清理旧蓝牙服务缓存，等待下一个唤醒窗口")
        # The same address exposes different GATT tables in normal and OTA
        # mode. A proxy may return the right UUID with an obsolete handle.
        capabilities = bytes(await asyncio.wait_for(
            client.read_gatt_char(characteristic), timeout=3
        ))
        if capabilities != bytes((2, 60, 3, 5)):
            await client.clear_cache()
            raise OtaError("已清理不匹配的唤醒通道缓存，等待重新发现")
        _LOGGER.debug("已确认普通模式唤醒通道，handle=%s", characteristic.handle)
        await asyncio.wait_for(
            client.write_gatt_char(
                characteristic, REMOTE_WAKE_REQUEST, response=True
            ),
            timeout=3,
        )
        # The acknowledged request changes the GATT table after reset. Drop the
        # normal-mode table now so the next connection discovers OTA directly.
        await client.clear_cache()
    except BleakError:
        if client is not None and client.is_connected:
            await client.clear_cache()
        raise
    finally:
        if client is not None and client.is_connected:
            try:
                await asyncio.wait_for(client.disconnect(), timeout=2)
            except (TimeoutError, BleakError, EOFError, OSError):
                _LOGGER.debug("唤醒连接已关闭或设备正在重启", exc_info=True)
