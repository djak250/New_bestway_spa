from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from datetime import datetime
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_id = entry.title.lower().replace(' ', '_')
    async_add_entities([
        ResetButton(hass, entry, "Reset Filter Date", "filter_last_change", device_id),
        ResetButton(hass, entry, "Reset Chlorine Date", "chlorine_last_add", device_id),
    ])

class ResetButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, hass, entry, name, key, device_id):
        super().__init__(coordinator)
        self._hass = hass
        self._entry = entry
        self._name = name
        self._key = key
        self._device_id = device_id

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._key}_reset_{self._entry.entry_id}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._entry.title,
            "manufacturer": "Bestway",
            "model": "Spa",
            "sw_version": self.hass.data[DOMAIN].get("manifest_version", "unknown"),
        }

    async def async_press(self):
        new_date = datetime.now().strftime("%Y-%m-%d")
        self._hass.data[DOMAIN][self._entry.entry_id][self._key] = new_date

        self.coordinator.data = {
            **self.coordinator.data,
            self._key: new_date
        }

        await self.coordinator.async_request_refresh()
