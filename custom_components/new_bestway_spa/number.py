from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import asyncio

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    async_add_entities([
        BestwaySpaTargetTemperature(coordinator, api, entry.title)
    ])

class BestwaySpaTargetTemperature(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, api, title):
        super().__init__(coordinator)
        self._api = api
        self._attr_name = f"{title} Target Temperature"
        self._attr_unique_id = f"{title.lower().replace(' ', '_')}_temperature_setting"
        self._attr_native_min_value = 20.0
        self._attr_native_max_value = 40.0
        self._attr_native_step = 0.5
        self._attr_native_unit_of_measurement = "°C"

    @property
    def native_value(self):
        return self.coordinator.data.get("temperature_setting")

    async def async_set_native_value(self, value: float):
        await self._api.set_state("temperature_setting", value)
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
