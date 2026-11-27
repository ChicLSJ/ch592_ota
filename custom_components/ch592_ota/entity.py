"""Shared helpers for CH592 OTA entities."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo

from .coordinator import Ch592OtaCoordinator


def build_device_info(coordinator: Ch592OtaCoordinator) -> DeviceInfo:
    """Link this integration to the BTHome device by Bluetooth address.

    The BTHome integration registers this peripheral with its Bluetooth
    connection. Older HA versions merge these into one device; newer versions
    expose linked devices while keeping each integration's device ownership.
    """
    return DeviceInfo(
        connections={(CONNECTION_BLUETOOTH, coordinator.address)},
        name=coordinator.entry.title,
        manufacturer="WCH",
        model="CH592 BLE Gas Meter",
        sw_version=coordinator.data.get("firmware_version"),
    )
