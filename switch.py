"""Support for Lutron Homeworks CCO switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomeworksData, HomeworksEntity
from .const import CONF_ADDR, CONF_CONTROLLER_ID, CONF_CCOS, DOMAIN
from .pyhomeworks.pyhomeworks import HW_CCO_CHANGED, Homeworks

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Homeworks CCO switches."""
    data: HomeworksData = hass.data[DOMAIN][entry.entry_id]
    controller = data.controller
    controller_id = entry.options[CONF_CONTROLLER_ID]
    entities = []
    for cco in entry.options.get(CONF_CCOS, []):
        entity = HomeworksCCO(
            controller,
            controller_id,
            cco[CONF_ADDR],
            cco[CONF_NAME],
        )
        entities.append(entity)
    async_add_entities(entities, True)

class HomeworksCCO(HomeworksEntity, SwitchEntity):
    """Homeworks CCO."""

    def __init__(
        self,
        controller: Homeworks,
        controller_id: str,
        addr: str,
        name: str,
    ) -> None:
        """Create device with Address and name."""
        super().__init__(controller, controller_id, addr, 0, None)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{controller_id}.{addr}")}, name=name
        )
        self._state = False

    async def async_added_to_hass(self) -> None:
        """Call when entity is added to Home Assistant."""
        signal = f"homeworks_entity_{self._controller_id}_{self._addr}"
        _LOGGER.debug("connecting %s", signal)
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal, self._update_callback)
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await self.hass.async_add_executor_job(
            self._controller.cco_close, self._addr
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await self.hass.async_add_executor_job(
            self._controller.cco_open, self._addr
        )

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._state

    @callback
    def _update_callback(self, msg_type: str, values: list[Any]) -> None:
        """Process device specific messages."""
        if msg_type == HW_CCO_CHANGED:
            self._state = values[1] == "CLOSED"
            self.async_write_ha_state()
