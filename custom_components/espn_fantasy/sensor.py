"""Sensor platform for ESPN Fantasy."""

from __future__ import annotations

import asyncio
import logging

from espn_api.football import League

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_ESPN_S2,
    CONF_LEAGUE_ID,
    CONF_SWID,
    CONF_TEAM_ID,
    CONF_YEAR,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESPN Fantasy sensors."""

    league = await asyncio.to_thread(
        League,
        league_id=entry.data[CONF_LEAGUE_ID],
        year=entry.data[CONF_YEAR],
        espn_s2=entry.data[CONF_ESPN_S2],
        swid=entry.data[CONF_SWID],
    )

    team_id = entry.data[CONF_TEAM_ID]

    team = next(
        (team for team in league.teams if team.team_id == team_id),
        None,
    )

    if team is None:
        _LOGGER.error("ESPN Fantasy team ID %s was not found", team_id)
        return

    async_add_entities(
        [
            ESPNFantasyTeamSensor(
                entry=entry,
                team=team,
            )
        ],
        True,
    )


class ESPNFantasyTeamSensor(SensorEntity):
    """ESPN Fantasy team sensor."""

    _attr_icon = "mdi:football"

    def __init__(self, entry: ConfigEntry, team) -> None:
        """Initialize the sensor."""

        self._team = team

        self._attr_name = team.team_name
        self._attr_unique_id = (
            f"espn_fantasy_{entry.data[CONF_LEAGUE_ID]}_"
            f"{team.team_id}_team"
        )

    @property
    def native_value(self):
        """Return the team's current record."""

        return f"{self._team.wins}-{self._team.losses}"

    @property
    def extra_state_attributes(self):
        """Return additional team information."""

        return {
            "team_id": self._team.team_id,
            "team_name": self._team.team_name,
            "wins": self._team.wins,
            "losses": self._team.losses,
            "ties": self._team.ties,
            "points_for": self._team.points_for,
            "points_against": self._team.points_against,
        }