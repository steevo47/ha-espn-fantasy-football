class ESPNFantasyCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error("You must define an entity");
    }

    this.config = config;
  }

  set hass(hass) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="espn-card"></div>
        </ha-card>
      `;

      this.content = this.querySelector(".espn-card");
    }

    const entity = hass.states[this.config.entity];

    if (!entity) {
      this.content.innerHTML = `
        <div class="error">
          Entity not found: ${this.config.entity}
        </div>
      `;
      return;
    }

    const a = entity.attributes;

    const team = a.team || "Team";
    const opponent = (a.opponent || "Opponent").trim();

    const score = this.formatNumber(a.score);
    const opponentScore = this.formatNumber(
      a.opponent_score
    );

    const projection = this.formatNumber(
      a.pregame_projection
    );

    const opponentProjection = this.formatNumber(
      a.opponent_pregame_projection
    );

    const lineup = a.lineup || [];
    const opponentLineup = a.opponent_lineup || [];

    let rows = "";

    lineup.forEach((player, index) => {
      const opp = opponentLineup[index];

      if (!opp) {
        return;
      }

      const leftWinner =
        Number(player.points) > Number(opp.points);

      const rightWinner =
        Number(opp.points) > Number(player.points);

      rows += `
        <div class="player left">
          <div class="player-name">
            ${this.escapeHtml(player.name)}
          </div>

          <div class="player-meta">
            ${this.escapeHtml(player.pro_team)}
            · Proj ${this.formatNumber(
              player.projected_points
            )}
          </div>
        </div>

        <div class="points ${
          leftWinner ? "winner" : ""
        }">
          ${this.formatNumber(player.points)}
        </div>

        <div class="position">
          ${this.escapeHtml(player.slot)}
        </div>

        <div class="points ${
          rightWinner ? "winner" : ""
        }">
          ${this.formatNumber(opp.points)}
        </div>

        <div class="player right">
          <div class="player-name">
            ${this.escapeHtml(opp.name)}
          </div>

          <div class="player-meta">
            ${this.escapeHtml(opp.pro_team)}
            · Proj ${this.formatNumber(
              opp.projected_points
            )}
          </div>
        </div>
      `;
    });

    const teamWinning =
      Number(a.score) > Number(a.opponent_score);

    const opponentWinning =
      Number(a.opponent_score) > Number(a.score);

    this.content.innerHTML = `
      <style>
        .espn-card {
          padding: 18px;
        }

        .week {
          text-align: center;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 1.5px;
          opacity: 0.55;
          margin-bottom: 14px;
        }

        .scoreboard {
          display: grid;
          grid-template-columns:
            minmax(0, 1fr)
            45px
            minmax(0, 1fr);
          align-items: center;
          margin-bottom: 20px;
        }

        .team {
          text-align: center;
          min-width: 0;
        }

        .team-name {
          font-size: 16px;
          font-weight: 600;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .score {
          font-size: 34px;
          font-weight: 700;
          line-height: 1.2;
          margin-top: 5px;
        }

        .score.leader {
          color: var(--primary-color);
        }

        .projection {
          margin-top: 3px;
          font-size: 11px;
          opacity: 0.6;
        }

        .vs {
          text-align: center;
          font-size: 11px;
          font-weight: 700;
          opacity: 0.45;
        }

        .divider {
          border-top:
            1px solid var(--divider-color);
          margin-bottom: 4px;
        }

        .lineup {
          display: grid;
          grid-template-columns:
            minmax(100px, 1fr)
            54px
            48px
            54px
            minmax(100px, 1fr);
          align-items: stretch;
        }

        .lineup > div {
          padding: 10px 5px;
          border-bottom:
            1px solid var(--divider-color);
          display: flex;
          justify-content: center;
          flex-direction: column;
        }

        .player {
          min-width: 0;
        }

        .player.left {
          text-align: left;
          align-items: flex-start;
        }

        .player.right {
          text-align: right;
          align-items: flex-end;
        }

        .player-name {
          width: 100%;
          font-size: 13px;
          font-weight: 600;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .player-meta {
          font-size: 10px;
          opacity: 0.55;
          margin-top: 2px;
        }

        .points {
          text-align: center;
          align-items: center;
          font-size: 14px;
          font-weight: 700;
        }

        .points.winner {
          color: var(--primary-color);
        }

        .position {
          text-align: center;
          align-items: center;
          font-size: 10px;
          font-weight: 700;
          opacity: 0.5;
        }

        .error {
          padding: 20px;
          color: var(--error-color);
        }

        @media (max-width: 600px) {
          .espn-card {
            padding: 12px;
          }

          .scoreboard {
            grid-template-columns:
              minmax(0, 1fr)
              32px
              minmax(0, 1fr);
          }

          .score {
            font-size: 28px;
          }

          .team-name {
            font-size: 13px;
          }

          .lineup {
            grid-template-columns:
              minmax(70px, 1fr)
              42px
              38px
              42px
              minmax(70px, 1fr);
          }

          .player-name {
            font-size: 11px;
          }

          .player-meta {
            font-size: 9px;
          }

          .points {
            font-size: 12px;
          }

          .position {
            font-size: 9px;
          }
        }
      </style>

      <div class="week">
        WEEK ${this.escapeHtml(a.week)}
      </div>

      <div class="scoreboard">

        <div class="team">
          <div class="team-name">
            ${this.escapeHtml(team)}
          </div>

          <div class="score ${
            teamWinning ? "leader" : ""
          }">
            ${score}
          </div>

          <div class="projection">
            Projected ${projection}
          </div>
        </div>

        <div class="vs">
          VS
        </div>

        <div class="team">
          <div class="team-name">
            ${this.escapeHtml(opponent)}
          </div>

          <div class="score ${
            opponentWinning ? "leader" : ""
          }">
            ${opponentScore}
          </div>

          <div class="projection">
            Projected ${opponentProjection}
          </div>
        </div>

      </div>

      <div class="divider"></div>

      <div class="lineup">
        ${rows}
      </div>
    `;
  }

  formatNumber(value) {
    const number = Number(value);

    if (Number.isNaN(number)) {
      return "0.00";
    }

    return number.toFixed(2);
  }

  escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value ?? "");
    return div.innerHTML;
  }

  getCardSize() {
    return 10;
  }
}

customElements.define(
  "espn-fantasy-card",
  ESPNFantasyCard
);

window.customCards = window.customCards || [];

window.customCards.push({
  type: "espn-fantasy-card",
  name: "ESPN Fantasy Card",
  description: "ESPN Fantasy Football matchup card",
});