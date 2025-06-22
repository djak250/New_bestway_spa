from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    async_add_entities([BestwaySpaThermostat(coordinator, api, entry.title)])

class BestwaySpaThermostat(CoordinatorEntity, ClimateEntity):
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = "°C"
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
        heater_state = self.coordinator.data.get("heater_state")
        power_state = self.coordinator.data.get("power_state")
        _LOGGER.debug(f"Heater state: {heater_state}, Power state: {power_state}")
        
        if heater_state is None or power_state != 1:
            return HVACMode.OFF
        
        # Based on API data: heater_state 4,5,6 = actively heating phases
        is_heating = heater_state in [4, 5, 6]
        _LOGGER.debug(f"Heater is actively heating (state {heater_state}): {is_heating}")
        return HVACMode.HEAT if is_heating else HVACMode.OFF

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self._api.set_state("temperature_setting", int(temperature))
            await asyncio.sleep(2)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.HEAT:
            await self._api.set_state("heater_state", 1)
        elif hvac_mode == HVACMode.OFF:
            await self._api.set_state("heater_state", 0)
            await asyncio.sleep(2)
            await self.coordinator.async_request_refresh()

# Make sure Home Assistant detects the setup function
__all__ = ["async_setup_entry"]
