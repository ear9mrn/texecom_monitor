"""Binary sensor platform for texecom_monitor."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription)

from .const import DOMAIN
from .coordinator import TexecomDataUpdateCoordinator
from .entity import TexecomMonitorEntity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="texecom_monitor",
        name="Texecom Monitor Binary Sensor",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        TexecomMonitorBinarySensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class TexecomMonitorBinarySensor(TexecomMonitorEntity, BinarySensorEntity):
    """texecom_monitor binary_sensor class."""

    def __init__(
        self,
        coordinator: TexecomDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.get("title", "") == "foo"
