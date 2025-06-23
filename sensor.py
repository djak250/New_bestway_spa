from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

SENSOR_TYPES = [
    ("water_temperature", "Water Temperature", "°C"),
    ("is_online", "Connection Status", None),
    ("temperature_unit", "Temperature Unit", None),
    ("warning", "Warning", None),
    ("error_code", "Error Code", None),
    ("hydrojet_state", "Hydrojet", None),
    ("ConnectType", "Connection Type", None),
    ("wifivertion", "WiFi Version", None),
    ("otastatus", "OTA Status", None),
    ("mcuversion", "MCU Version", None),
    ("trdversion", "TRD Version", None)
]

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    async_add_entities([
        BestwaySpaSensor(coordinator, key, name, unit, entry.title)
        for key, name, unit in SENSOR_TYPES
    ])

class BestwaySpaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit, title):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"{title} {name}"
        self._attr_unique_id = f"{title.lower().replace(' ', '_')}_{key}"
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def native_unit_of_measurement(self):
        if self._key == "water_temperature":
            unit_code = self.coordinator.data.get("temperature_unit", 1)
            return "°F" if unit_code == 0 else "°C"
        return None
