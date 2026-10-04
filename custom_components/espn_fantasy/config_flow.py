"""Config flow for ESPN Fantasy."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME

from .api import ESPNFantasyAPI
from .const import (
    CONF_ESPN_S2,
    CONF_LEAGUE_ID,
    CONF_SWID,
    CONF_TEAM_ID,
    CONF_YEAR,
    DEFAULT_YEAR,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ESPNFantasyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ESPN Fantasy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""

        errors = {}

        if user_input is not None:
            try:
                api = ESPNFantasyAPI(
                    league_id=user_input[CONF_LEAGUE_ID],
                    year=user_input[CONF_YEAR],
                    espn_s2=user_input[CONF_ESPN_S2],
                    swid=user_input[CONF_SWID],
                )

                league = await api.async_connect()

                # Verify that the requested team actually exists.
                team_id = user_input[CONF_TEAM_ID]

                team = next(
                    (
                        team
                        for team in league.teams
                        if team.team_id == team_id
                    ),
                    None,
                )

                if team is None:
                    errors["base"] = "team_not_found"

                else:
                    await self.async_set_unique_id(
                        f"{user_input[CONF_LEAGUE_ID]}_{team_id}"
                    )
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input,
                    )

            except Exception:
                _LOGGER.exception("Unable to connect to ESPN Fantasy")
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default="ESPN Fantasy",
                ): str,
                vol.Required(CONF_LEAGUE_ID): int,
                vol.Required(CONF_TEAM_ID): int,
                vol.Required(
                    CONF_YEAR,
                    default=DEFAULT_YEAR,
                ): int,
                vol.Required(CONF_SWID): str,
                vol.Required(CONF_ESPN_S2): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )