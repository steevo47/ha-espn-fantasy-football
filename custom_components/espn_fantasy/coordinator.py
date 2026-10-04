"""Data coordinator for ESPN Fantasy."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_ESPN_S2,
    CONF_LEAGUE_ID,
    CONF_SWID,
    CONF_TEAM_ID,
    CONF_YEAR,
)

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=5)


def _load_league(
    league_id: int,
    year: int,
    espn_s2: str,
    swid: str,
):
    """Load ESPN league data in an executor thread."""

    from espn_api.football import League

    return League(
        league_id=league_id,
        year=year,
        espn_s2=espn_s2,
        swid=swid,
    )


class ESPNFantasyCoordinator(DataUpdateCoordinator):
    """Coordinate ESPN Fantasy data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            name="ESPN Fantasy",
            update_interval=UPDATE_INTERVAL,
        )

        self.entry = entry
        self.league = None

    async def _async_update_data(self):
        """Fetch data from ESPN."""

        try:
            league = await asyncio.to_thread(
                _load_league,
                self.entry.data[CONF_LEAGUE_ID],
                self.entry.data[CONF_YEAR],
                self.entry.data[CONF_ESPN_S2],
                self.entry.data[CONF_SWID],
            )

            team_id = self.entry.data[CONF_TEAM_ID]

            team = next(
                (
                    team
                    for team in league.teams
                    if team.team_id == team_id
                ),
                None,
            )

            if team is None:
                raise UpdateFailed(
                    f"Team ID {team_id} was not found"
                )

            # Get the current week's box scores.
            box_scores = await asyncio.to_thread(
                league.box_scores
            )

            # Find the matchup containing our configured team.
            matchup = next(
                (
                    box_score
                    for box_score in box_scores
                    if (
                        box_score.home_team
                        and box_score.home_team.team_id == team_id
                    )
                    or (
                        box_score.away_team
                        and box_score.away_team.team_id == team_id
                    )
                ),
                None,
            )

            self.league = league

            return {
                "league": league,
                "team": team,
                "matchup": matchup,
            }

        except UpdateFailed:
            raise

        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with ESPN: {err}"
            ) from err