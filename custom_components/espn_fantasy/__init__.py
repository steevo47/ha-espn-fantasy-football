"""ESPN Fantasy integration for Home Assistant."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import ESPNFantasyCoordinator

PLATFORMS = ["sensor"]

CARD_URL = "/espn_fantasy/espn-fantasy-card.js"
CARD_PATH = Path(__file__).parent / "www" / "espn-fantasy-card.js"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up ESPN Fantasy from a config entry."""

    coordinator = ESPNFantasyCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Serve the bundled Lovelace card.
    if not hass.data.get("espn_fantasy_frontend_registered"):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    CARD_URL,
                    str(CARD_PATH),
                    False,
                )
            ]
        )

        hass.data["espn_fantasy_frontend_registered"] = True

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload ESPN Fantasy config entry."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )