import logging
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, API_URL

class GrünstromindexConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for Grünstromindex."""
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Grünstromindex", data=user_input)
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("zip_code"): str,
                vol.Optional("api_token"): str,
            }),
            errors=errors,
        )
