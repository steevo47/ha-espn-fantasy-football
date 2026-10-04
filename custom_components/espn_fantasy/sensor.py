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
            ESPNFantasyTeamSensor(coordinator, entry),
            ESPNFantasyMatchupSensor(coordinator, entry),
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

    def _get_matchup_data(self):
        """Determine our side of the matchup."""

        matchup = self.coordinator.data.get("matchup")

        if matchup is None:
            return None

        if matchup.home_team.team_id == self._team_id:
            return {
                "team": matchup.home_team,
                "opponent": matchup.away_team,
                "score": matchup.home_score,
                "opponent_score": matchup.away_score,
                "lineup": matchup.home_lineup,
                "opponent_lineup": matchup.away_lineup,
            }

        return {
            "team": matchup.away_team,
            "opponent": matchup.home_team,
            "score": matchup.away_score,
            "opponent_score": matchup.home_score,
            "lineup": matchup.away_lineup,
            "opponent_lineup": matchup.home_lineup,
        }

    @staticmethod
    def _starting_lineup(lineup):
        """Return starting players, excluding bench and IR."""

        return [
            player
            for player in lineup
            if player.slot_position not in ("BE", "IR")
        ]

    @staticmethod
    def _pregame_projection(lineup):
        """Calculate ESPN pregame projection."""

        return round(
            sum(
                player.projected_points or 0
                for player in lineup
                if player.slot_position not in ("BE", "IR")
            ),
            2,
        )

    @staticmethod
    def _lineup_attributes(lineup):
        """Convert starting lineup to HA-friendly data."""

        players = []

        for player in lineup:
            if player.slot_position in ("BE", "IR"):
                continue

            players.append(
                {
                    "name": player.name,
                    "slot": player.slot_position,
                    "position": player.position,
                    "pro_team": player.proTeam,
                    "points": round(player.points or 0, 2),
                    "projected_points": round(
                        player.projected_points or 0,
                        2,
                    ),
                }
            )

        return players

    @property
    def native_value(self):
        """Return current matchup score."""

        data = self._get_matchup_data()

        if data is None:
            return "No matchup"

        return (
            f"{data['score']:.2f} - "
            f"{data['opponent_score']:.2f}"
        )

    @property
    def extra_state_attributes(self):
        """Return current matchup information."""

        matchup = self.coordinator.data.get("matchup")
        league = self.coordinator.data.get("league")
        data = self._get_matchup_data()

        if matchup is None or data is None:
            return {}

        lineup = self._starting_lineup(data["lineup"])
        opponent_lineup = self._starting_lineup(
            data["opponent_lineup"]
        )

        return {
            "week": league.current_week,

            "team": data["team"].team_name,
            "team_id": data["team"].team_id,
            "score": round(data["score"], 2),
            "pregame_projection": self._pregame_projection(
                lineup
            ),

            "opponent": data["opponent"].team_name,
            "opponent_team_id": data["opponent"].team_id,
            "opponent_score": round(
                data["opponent_score"],
                2,
            ),
            "opponent_pregame_projection":
                self._pregame_projection(
                    opponent_lineup
                ),

            "home_team": matchup.home_team.team_name,
            "home_score": round(matchup.home_score, 2),

            "away_team": matchup.away_team.team_name,
            "away_score": round(matchup.away_score, 2),

            "lineup": self._lineup_attributes(lineup),

            "opponent_lineup":
                self._lineup_attributes(
                    opponent_lineup
                ),
        }