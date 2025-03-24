import logging
import asyncio
import aiohttp
import async_timeout
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.sensor import SensorEntity
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Grünstromindex integration from a config entry."""
    session = async_get_clientsession(hass)
    coordinator = GrünstromindexDataUpdateCoordinator(hass, session, entry.data)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    sensors = [
        CO2AverageSensor(coordinator),
        CO2StandardSensor(coordinator),
        CO2OekostromSensor(coordinator),
        GSISensor(coordinator),
        WindPowerSensor(coordinator),
        SolarPowerSensor(coordinator)
    ]
    
    async_add_entities(sensors)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

class GrünstromindexDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Grünstromindex API."""
    def __init__(self, hass, session, config):
        """Initialize the coordinator."""
        self.session = session
        self.zip_code = config.get("zip_code")
        self.api_token = config.get("api_token")
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )
    
    async def _async_update_data(self):
        """Fetch data from API."""
        params = {"zip": self.zip_code}
        if self.api_token:
            params["token"] = self.api_token
        
        try:
            async with async_timeout.timeout(10):
                response = await self.session.get(API_URL, params=params)
                response.raise_for_status()
                data = await response.json()
                return data
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"API request failed: {err}")
        except asyncio.TimeoutError:
            raise UpdateFailed("API request timed out")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")

class BaseSensor(SensorEntity):
    """Base class for Grünstromindex sensors."""
    _attr_state_class = "measurement"
    _attr_icon = "mdi:molecule-co2"  # Set the icon here
    def __init__(self, coordinator, name, key, unit):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_name = name
        self._attr_unique_id = f"{key}_{coordinator.zip_code}"
        self.key = key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.zip_code)},
            "name": f"Grünstromindex {coordinator.zip_code}",
            "manufacturer": "Corrently",
            "model": "Energy Sensor",
        }
        self._attr_should_poll = False
        self.coordinator.async_add_listener(self.async_write_ha_state)
    
    @property
    def state(self):
        """Return the sensor value."""
        if "forecast" in self.coordinator.data and self.coordinator.data["forecast"]:
            return self.coordinator.data["forecast"][0].get(self.key, None)
        return None

class CO2AverageSensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "CO2 Average", "co2_avg", "gCO2eq/kWh")

class CO2StandardSensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "CO2 Standard", "co2_g_standard", "gCO2eq/kWh")

class CO2OekostromSensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "CO2 Ökostrom", "co2_g_oekostrom", "gCO2eq/kWh")

class GSISensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "Green Power Index", "gsi", "%")

class WindPowerSensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "Wind Power Contribution", "ewind", "%")

class SolarPowerSensor(BaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "Solar Power Contribution", "esolar", "%")
