from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from .const import DOMAIN
from .spa_api import BestwaySpaAPI, authenticate
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "number", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bestway Spa from a config entry."""

    session = aiohttp.ClientSession()

    token = await authenticate(session, entry.data)
    if not token:
        _LOGGER.error("Authentication failed: No token returned")
        return False

    api = BestwaySpaAPI(session, {**entry.data, "token": token})

    async def async_update_data():
        try:
            return await api.get_status()
        except Exception as err:
            raise UpdateFailed(f"Error fetching spa data: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Bestway Spa",
        update_method=async_update_data,
        update_interval=timedelta(seconds=60),
    )

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
