"""Sensor platform for ESPN Fantasy."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_LEAGUE_ID
from .coordinator import ESPNFantasyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESPN Fantasy sensors."""

    coordinator: ESPNFantasyCoordinator = entry.runtime_data

    async_add_entities(
        [
            ESPNFantasyTeamSensor(
                coordinator,
                entry,
            )
        ]
    )


class ESPNFantasyTeamSensor(
    CoordinatorEntity[ESPNFantasyCoordinator],
    SensorEntity,
):
    """ESPN Fantasy team sensor."""

    _attr_icon = "mdi:football"

    def __init__(
        self,
        coordinator: ESPNFantasyCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(coordinator)

        team = coordinator.data["team"]

        self._attr_name = team.team_name
        self._attr_unique_id = (
            f"espn_fantasy_{entry.data[CONF_LEAGUE_ID]}_"
            f"{team.team_id}_team"
        )

    @property
    def native_value(self):
        """Return the team's current record."""

        team = self.coordinator.data["team"]

        if team.ties:
            return f"{team.wins}-{team.losses}-{team.ties}"

        return f"{team.wins}-{team.losses}"

    @property
    def extra_state_attributes(self):
        """Return additional team information."""

        team = self.coordinator.data["team"]

        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "wins": team.wins,
            "losses": team.losses,
            "ties": team.ties,
            "points_for": team.points_for,
            "points_against": team.points_against,
        }