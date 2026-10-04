"""ESPN Fantasy API client."""

from __future__ import annotations

import asyncio


def _load_league(
    league_id: int,
    year: int,
    espn_s2: str,
    swid: str,
):
    """Load an ESPN Fantasy league."""

    from espn_api.football import League

    return League(
        league_id=league_id,
        year=year,
        espn_s2=espn_s2,
        swid=swid,
    )


class ESPNFantasyAPI:
    """Wrapper for the ESPN Fantasy Football API."""

    def __init__(
        self,
        league_id: int,
        year: int,
        espn_s2: str,
        swid: str,
    ) -> None:
        """Initialize ESPN Fantasy API."""

        self.league_id = league_id
        self.year = year
        self.espn_s2 = espn_s2
        self.swid = swid
        self.league = None

    async def async_connect(self):
        """Connect to ESPN and load league data."""

        self.league = await asyncio.to_thread(
            _load_league,
            self.league_id,
            self.year,
            self.espn_s2,
            self.swid,
        )

        return self.league