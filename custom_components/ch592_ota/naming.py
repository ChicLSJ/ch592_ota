"""Give the paired BTHome version and counter distinct presentation."""

from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er


@callback
def async_register_version_name(hass, entry):
    """Set meter defaults while preserving custom names and icons."""
    registry = er.async_get(hass)
    address = entry.data["address"].upper()

    @callback
    def update_name(event=None):
        if event is not None and event.data.get("action") != "create":
            return
        language = str(hass.config.language or "zh-Hans")
        name = "固件" if language.startswith("zh") else "Firmware"
        for key, icon in (("text", "mdi:chip"), ("count", "mdi:counter")):
            entity_id = registry.async_get_entity_id("sensor", "bthome", f"{address}-{key}")
            entity = registry.async_get(entity_id) if entity_id else None
            if entity is None:
                continue
            changes = {}
            if key == "text" and entity.name in (None, "固件", "Firmware") and entity.name != name:
                changes["name"] = name
            if entity.icon is None:
                changes["icon"] = icon
            if changes:
                registry.async_update_entity(entity_id, **changes)

    entry.async_on_unload(hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, update_name))
    update_name()
