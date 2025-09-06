import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["device_name"], data=user_input)

        schema = vol.Schema({
            vol.Required("device_name"): str,
            vol.Required("visitor_id"): str,
            vol.Required("registration_id"): str,
            vol.Optional("device_id"): str,
            vol.Optional("product_id"): str,
            vol.Optional("push_type", default="fcm"): vol.In(["fcm", "apns"]),
            vol.Optional("client_id"): str,
            vol.Optional("api_host", default="smarthub-eu.bestwaycorp.com"): str
            vol.Optional("location", default="GB"): str
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
