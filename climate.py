from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    async_add_entities([BestwaySpaThermostat(coordinator, api, entry.title)])

class BestwaySpaThermostat(CoordinatorEntity, ClimateEntity):
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_min_temp = 20
    _attr_max_temp = 40

    def __init__(self, coordinator, api, title):
        super().__init__(coordinator)
        self._api = api
        self._attr_name = f"{title} Thermostat"
        self._attr_unique_id = f"{title.lower().replace(' ', '_')}_thermostat"

    @property
    def current_temperature(self):
        return self.coordinator.data.get("water_temperature")

    @property
    def target_temperature(self):
        return self.coordinator.data.get("temperature_setting")

    @property
    def hvac_mode(self):
        return HVACMode.HEAT if self.coordinator.data.get("heater_state") else HVACMode.OFF

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self._api.set_state("temperature_setting", int(temperature))
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.HEAT:
            await self._api.set_state("heater_state", 1)
        elif hvac_mode == HVACMode.OFF:
            await self._api.set_state("heater_state", 0)
        await self.coordinator.async_request_refresh()
