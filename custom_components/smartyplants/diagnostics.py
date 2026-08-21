"""Diagnostics support for SmartyPlants."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_API_KEY, CONF_WEBHOOK_ID
from homeassistant.core import HomeAssistant

from .const import CONF_WEBHOOK_SECRET
from .coordinator import SmartyPlantsConfigEntry, is_stale, setup_status

# The key and secret authenticate the account, and the webhook id is a public
# URL component, so none of them belong in a shared diagnostics file.
TO_REDACT = {CONF_API_KEY, CONF_WEBHOOK_SECRET, CONF_WEBHOOK_ID}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: SmartyPlantsConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "webhook_configured": CONF_WEBHOOK_SECRET in entry.data,
        "last_update_success": coordinator.last_update_success,
        "sensors": [
            {
                # Ids identify rows in the SmartyPlants account, so they are
                # reported as a count and shape rather than verbatim.
                "status": setup_status(sensor),
                "is_online": sensor.get("isOnline"),
                "is_stale": is_stale(sensor),
                "is_plant_only": bool(sensor.get("isPlantOnly")),
                "has_plant": bool(sensor.get("plant")),
                "environment": (sensor.get("plant") or {}).get("environment"),
                "battery_percentage": sensor.get("batteryPercentage"),
                "last_data_received": sensor.get("lastDataReceived"),
                "health": sensor.get("health"),
                "readings": sensor.get("readings"),
            }
            for sensor in (coordinator.data or {}).values()
        ],
    }
