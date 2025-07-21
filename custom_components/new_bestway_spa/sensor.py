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
    ("connect_type", "Connection Type", None),
    ("wifi_version", "WiFi Version", None),
    ("ota_status", "OTA Status", None),
    ("mcu_version", "MCU Version", None),
    ("trd_version", "TRD Version", None)
]

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_id = entry.title.lower().replace(' ', '_')
    async_add_entities([
        BestwaySpaSensor(coordinator, key, name, unit, entry.title, device_id)
        for key, name, unit in SENSOR_TYPES
    ])

class BestwaySpaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit, title, device_id):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"{title} {name}"
        self._attr_unique_id = f"{device_id}_{key}"
        self._device_id = device_id
        self._attr_native_unit_of_measurement = unit

        # enable long-term statistics for water temperature
        if self._key == "water_temperature":
            self._attr_device_class = "temperature"
            self._attr_state_class = "measurement"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._attr_name.split(" ")[0],  # lub np. self._device_id
            "manufacturer": "Bestway",
            "model": "Spa",
            "sw_version": self.hass.data[DOMAIN].get("manifest_version", "unknown")
        }

    @property
    def native_value(self):
        if self._key == "temperature_unit":
            raw = self.coordinator.data.get("temperature_unit", 1)
            return "°F" if raw == 0 else "°C" 
        return self.coordinator.data.get(self._key)

    @property
    def native_unit_of_measurement(self):
        if self._key == "water_temperature":
            unit_code = self.coordinator.data.get("temperature_unit", 1)
            return "°F" if unit_code == 0 else "°C"
        return self._attr_native_unit_of_measurement
