"""Sensor platform for texecom_monitor."""
from __future__ import annotations

from homeassistant.components.sensor import (SensorEntity,
                                             SensorEntityDescription)

from .const import DOMAIN
from .coordinator import TexecomDataUpdateCoordinator
from .entity import TexecomMonitorEntity
#import time

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="texecom_monitor",
        name="Integration Sensor",
        #icon="mdi:format-quote-close",
        icon="mdi:door-closed",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        TexecomMonitorSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class TexecomMonitorSensor(TexecomMonitorEntity, SensorEntity):
    """texecom_monitor Sensor class."""

    def __init__(
        self,
        coordinator: TexecomDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        #print(self.coordinator.data.get("body"))
        #t = time.localtime()
        #current_time = time.strftime("%H:%M:%S", t)
        #print(current_time)
        #return self.coordinator.data.get("body")
        return "66"
