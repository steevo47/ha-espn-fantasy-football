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
            ),
            ESPNFantasyMatchupSensor(
                coordinator,
                entry,
            ),    
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
class ESPNFantasyMatchupSensor(
    CoordinatorEntity[ESPNFantasyCoordinator],
    SensorEntity,
):
    """Current ESPN Fantasy matchup sensor."""

    _attr_icon = "mdi:scoreboard"

    def __init__(
        self,
        coordinator: ESPNFantasyCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the matchup sensor."""

        super().__init__(coordinator)

        team = coordinator.data["team"]

        self._team_id = team.team_id

        self._attr_name = f"{team.team_name} Matchup"
        self._attr_unique_id = (
            f"espn_fantasy_{entry.data[CONF_LEAGUE_ID]}_"
            f"{team.team_id}_matchup"
        )

    @property
    def native_value(self):
        """Return current matchup score."""

        matchup = self.coordinator.data.get("matchup")

        if matchup is None:
            return "No matchup"

        if matchup.home_team.team_id == self._team_id:
            my_score = matchup.home_score
            opponent_score = matchup.away_score
        else:
            my_score = matchup.away_score
            opponent_score = matchup.home_score

        return f"{my_score:.2f} - {opponent_score:.2f}"

    @property
    def extra_state_attributes(self):
        """Return current matchup information."""

        matchup = self.coordinator.data.get("matchup")

        if matchup is None:
            return {}

        if matchup.home_team.team_id == self._team_id:
            my_team = matchup.home_team
            opponent = matchup.away_team
            my_score = matchup.home_score
            opponent_score = matchup.away_score
        else:
            my_team = matchup.away_team
            opponent = matchup.home_team
            my_score = matchup.away_score
            opponent_score = matchup.home_score

        return {
            "team": my_team.team_name,
            "team_id": my_team.team_id,
            "score": my_score,
            "opponent": opponent.team_name,
            "opponent_team_id": opponent.team_id,
            "opponent_score": opponent_score,
            "home_team": matchup.home_team.team_name,
            "home_score": matchup.home_score,
            "away_team": matchup.away_team.team_name,
            "away_score": matchup.away_score,
        }