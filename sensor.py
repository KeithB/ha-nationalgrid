"""National Grid DFS integration."""
from __future__ import annotations

## HA imports
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_NAME,
    CONF_NAME
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType
)
import voluptuous as vol

from typing import Dict
from datetime import timedelta
from .nationalGrid import ( NationalGridClient )
from .const import ( ATTR_DFS_SESSION_START, ATTR_DFS_SESSION_END )

## Note - This makes sure state/attribute data is current but actual polling intervals to
## National grid are controlled by the client
SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string
    }
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    NGclient = NationalGridClient(session)
    
    sensors = [NationalGridDFSSession(NGclient, config)]
    
    async_add_entities(sensors, update_before_add=True)


class NationalGridDFSSession ( Entity ):
  def __init__(self, NGclient: NationalGridClient, config: ConfigType ):
    super().__init__()
    self._NGclient = NGclient
    self._name = config[CONF_NAME]+'_DFS'
    self._state = None
    self._available = True

  @property
  def name(self) -> str:
    """Return the name of the entity."""
    return self._name

  @property
  def available(self) -> bool:
    return self._available

  @property
  def state(self) -> str:
    return self._state

  @property
  def extra_state_attributes(self) -> Dict[str, Any]:
    client = self._NGclient
    return {
        ATTR_DFS_SESSION_START: client.get_dfs_session_start(),
        ATTR_DFS_SESSION_END: client.get_dfs_session_end()
    }

  async def async_update(self):
    client = self._NGclient
    await client.async_get_todays_dfs_requirements()

    self._state = client.get_current_dfs_status()




