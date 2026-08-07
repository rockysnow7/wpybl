from __future__ import annotations
from datetime import datetime
from enum import Enum
from play import Play
from pydantic import BaseModel, Field, BeforeValidator
from team import Team
from typing import Annotated, Any


class GameStatus(str, Enum):
    FINAL = "Final"
    UPCOMING = "Upcoming"


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
    tracking_activity: list | None = None

    @staticmethod
    def from_json(json: dict) -> Game:
        if "boxscore" not in json:
            raise ValueError("JSON does not contain a boxscore")
        return Game.model_validate(json["boxscore"])
