"""Binary sensor entities for SmartyPlants."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import (
    SmartyPlantsConfigEntry,
    SmartyPlantsCoordinator,
    is_stale,
    is_usable,
)
from .entity import SmartyPlantsEntity, async_setup_dynamic_entities

# Read-only and coordinator-driven, so updates need not be serialised.
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class SmartyPlantsBinarySensorDescription(BinarySensorEntityDescription):
    """Describes one SmartyPlants binary sensor."""

    is_on_fn: Callable[[dict[str, Any]], bool | None]
    stale_sensitive: bool = True
    # Skipped for plants that have no sensor, where the state has no meaning.
    requires_sensor: bool = True


BINARY_SENSOR_TYPES: tuple[SmartyPlantsBinarySensorDescription, ...] = (
    # Connectivity must survive staleness — it is how the user sees the problem.
    # A sensor that has not reported within the staleness window is not
    # meaningfully connected, so staleness counts as disconnected here.
    SmartyPlantsBinarySensorDescription(
        key="online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        stale_sensitive=False,
        is_on_fn=is_usable,
    ),
    SmartyPlantsBinarySensorDescription(
        key="stale",
        translation_key="stale",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        stale_sensitive=False,
        is_on_fn=is_stale,
    ),
    SmartyPlantsBinarySensorDescription(
        key="needs_attention",
        translation_key="needs_attention",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda sensor: not (sensor.get("health") or {}).get("isHealthy", True),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartyPlantsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Create the binary sensors for every physical sensor."""
    coordinator = entry.runtime_data

    async_setup_dynamic_entities(
        entry,
        coordinator,
        async_add_entities,
        lambda sensor_id: (
            SmartyPlantsBinarySensor(coordinator, sensor_id, description)
            for description in BINARY_SENSOR_TYPES
            if description.requires_sensor is False
            or not coordinator.data[sensor_id].get("isPlantOnly")
        ),
    )


class SmartyPlantsBinarySensor(SmartyPlantsEntity, BinarySensorEntity):
    """Connectivity, staleness and health state for a SmartyPlants sensor."""

    entity_description: SmartyPlantsBinarySensorDescription

    def __init__(
        self,
        coordinator: SmartyPlantsCoordinator,
        sensor_id: str,
        description: SmartyPlantsBinarySensorDescription,
    ) -> None:
        """Initialise the entity."""
        super().__init__(coordinator, sensor_id)
        self.entity_description = description
        self._attr_unique_id = f"{sensor_id}_{description.key}"

    @property
    @override
    def available(self) -> bool:
        """Follow the shared availability rule for this entity's description."""
        return self._availability_for(
            stale_sensitive=self.entity_description.stale_sensitive,
            requires_sensor=self.entity_description.requires_sensor,
        )

    @property
    @override
    def is_on(self) -> bool | None:
        """Return the current state."""
        return self.entity_description.is_on_fn(self.sensor)
