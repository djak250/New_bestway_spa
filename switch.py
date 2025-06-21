from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

SWITCH_TYPES = [
    ("power_state", "Spa Power"),
    ("filter_state", "Filter"),
    ("heater_state", "Heater"),
    ("wave_state", "Bubbles / Wave")
]

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    async_add_entities([
        BestwaySpaSwitch(coordinator, api, key, name, entry.title)
        for key, name in SWITCH_TYPES
    ])

class BestwaySpaSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, api, key, name, title):
        super().__init__(coordinator)
        self._api = api
        self._key = key
        self._attr_name = f"{title} {name}"
        self._attr_unique_id = f"{title.lower().replace(' ', '_')}_{key}"

    @property
    def is_on(self):
        if self._key == "filter_state":
            # API returns 2 when filter is active
            return self.coordinator.data.get("filter_state") == 2
        elif self._key == "heater_state":
            # API returns 4,5,6 when heater is in various heating phases
            heater_state = self.coordinator.data.get("heater_state")
            return heater_state in [4, 5, 6]
        return self.coordinator.data.get(self._key) == 1

    async def async_turn_on(self, **kwargs):
        await self._api.set_state(self._key, 1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self._api.set_state(self._key, 0)
        await self.coordinator.async_request_refresh()
