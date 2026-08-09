from __future__ import annotations
from datetime import datetime
from enum import Enum
from .play import Play
from pydantic import BaseModel, Field
from .team import Team, Player
from .tracking_activity import TrackingActivity
from typing import Annotated

import pandas as pd


class GameStatus(str, Enum):
    UNKNOWN = "unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    FINAL = "Final"
    UPCOMING = "Upcoming"

    @classmethod
    def _missing_(cls, value) -> GameStatus:
        return GameStatus.UNKNOWN


class Status(BaseModel):
    complete: bool
    inning: Annotated[int, Field(ge=0)]
    half: str
    batting_team_id: str
    outs: Annotated[int, Field(ge=0)]
    balls: Annotated[int, Field(ge=0)]
    strikes: Annotated[int, Field(ge=0)]
    batter_name: str
    pitcher_name: str
    first_base: str
    second_base: str
    third_base: str
    bases_occupied: list[Annotated[int, Field(ge=1, le=3)]]
    bases_loaded: bool
    away_runs: Annotated[int, Field(ge=0)]
    home_runs: Annotated[int, Field(ge=0)]


class Game(BaseModel):
    game_id: str
    provider: str
    game_status: GameStatus
    source_updated_at: datetime
    fetched_at: datetime
    status: Status
    teams: list[Team]
    plays: list[Play]
    tracking_activity: list[TrackingActivity] | None = None

    @staticmethod
    def from_json(json: dict) -> Game:
        if "boxscore" not in json:
            raise ValueError("JSON does not contain a boxscore")
        return Game.model_validate(json["boxscore"])

    def get_player(self, player_name: str) -> Player | None:
        for team in self.teams:
            for player in team.players:
                if player.name == player_name:
                    return player

    def plays_to_csv(self, path: str) -> None:
        """Converts the game's plays to a CSV file and saves it to the specified path."""

        rows = [play.to_csv_row() for play in self.plays]
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False)
