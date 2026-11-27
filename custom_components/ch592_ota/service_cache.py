"""Discard mode-specific ESPHome service tables before explicit connections."""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth

_LOGGER = logging.getLogger(__name__)


def discard_mode_services(hass, address: str) -> int:
    """Clear only this meter's host cache, without any radio or proxy request.

    ESPHome REMOTE_CACHING can return the host's old table even when connect
    disables cache use. Its connector carries the shared cache in client_data.
    Feature detection keeps other adapters and changed connector layouts on
    the existing checked-discovery fallback. Never run this from polling.
    """
    lookup = getattr(bluetooth, "async_scanner_devices_by_address", None)
    if lookup is None:
        return 0
    target = int(address.replace(":", ""), 16)
    cleared = set()
    for path in lookup(hass, address, connectable=True):
        connector = getattr(path.scanner, "connector", None)
        factory = getattr(connector, "client", None)
        client_type = getattr(factory, "func", None)
        if not getattr(client_type, "__module__", "").startswith("bleak_esphome."):
            continue
        data = getattr(factory, "keywords", {}).get("client_data")
        cache = getattr(getattr(data, "bluetooth_device", None), "cache", None)
        clear = getattr(cache, "clear_gatt_services_cache", None)
        if not callable(clear) or id(cache) in cleared:
            continue
        clear(target)
        cleared.add(id(cache))
    if cleared:
        _LOGGER.debug("Discarded %s mode service caches for %s", len(cleared), address)
    return len(cleared)
