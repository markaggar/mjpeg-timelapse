import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Mjpeg Timelapse from a config entry."""
    # Store the config entry ID in the data dict
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    # Ensure that existing entities are updated with the new config
    registry = async_get_entity_registry(hass)
    entity_id = registry.async_get_entity_id("camera", DOMAIN, entry.entry_id)
    if entity_id:
        registry.async_update_entity(entity_id, config_entry_id=entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, ["camera"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "camera")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
