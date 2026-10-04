"""ESPN Fantasy API client."""

from __future__ import annotations

import asyncio

from espn_api.football import League


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
        self.league: League | None = None

    async def async_connect(self) -> League:
        """Connect to ESPN and load league data."""

        self.league = await asyncio.to_thread(
            League,
            league_id=self.league_id,
            year=self.year,
            espn_s2=self.espn_s2,
            swid=self.swid,
        )

        return self.league