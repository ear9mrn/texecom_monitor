"""DataUpdateCoordinator for texecom_monitor."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)
from .texecom_connect.texecom_connect import texecom_cestron as texe

from .api import (TexecomMonitorApiClient,
                  TexecomMonitorApiClientAuthenticationError,
                  TexecomMonitorApiClientError)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class TexecomDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: TexecomMonitorApiClient,
    ) -> None:
        """Initialize."""
        self.client = client

        self.conn = texe("192.168.1.218",data_type="basic")
        self.conn.add_callback(self.print_info)
        self.conn.listen()

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=20),
        )

    def print_info(self,info):
        print(f"x{info}")

    async def _async_update_data(self):
        """Update data via library."""
        return "22"
        #try:
        #    return await self.client.async_get_data()
        #except TexecomMonitorApiClientAuthenticationError as exception:
        #    raise ConfigEntryAuthFailed(exception) from exception
        #except TexecomMonitorApiClientError as exception:
        #    raise UpdateFailed(exception) from exception
