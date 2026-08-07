from __future__ import annotations
from enum import Enum
from pydantic import AfterValidator, BaseModel, Field, BeforeValidator
from typing import Annotated, Any

import re


class Side(str, Enum):
    AWAY = "away"
    HOME = "home"


class TeamRecord(BaseModel):
    wins: Annotated[int, Field(ge=0)]
    losses: Annotated[int, Field(ge=0)]

    @staticmethod
    def before_validator(value: Any) -> TeamRecord:
        if not isinstance(value, str):
            raise TypeError("Team record must be a string")
        if not re.match(r"^\d+-\d+$", value):
            raise ValueError("Team record must be in the format of <wins>-<losses>")

        wins, losses = value.split("-")
        return TeamRecord(wins=int(wins), losses=int(losses))


class LineScoreInning(BaseModel):
    inning: Annotated[int, Field(ge=1)]
    runs: Annotated[int, Field(ge=0)]


class TeamTotalsBatting(BaseModel):
    at_bats: Annotated[int, Field(ge=0, alias="ab"), BeforeValidator(int)] = 0
    bases_on_balls: Annotated[int, Field(ge=0, alias="bb"), BeforeValidator(int)] = 0
    intentional_bases_on_balls: Annotated[
        int, Field(ge=0, alias="ibb"), BeforeValidator(int)
    ] = 0
    hits: Annotated[int, Field(ge=0, alias="h"), BeforeValidator(int)] = 0
    doubles: Annotated[int, Field(ge=0, alias="double"), BeforeValidator(int)] = 0
    triples: Annotated[int, Field(ge=0, alias="triple"), BeforeValidator(int)] = 0
    home_runs: Annotated[int, Field(ge=0, alias="hr"), BeforeValidator(int)] = 0
    ground_balls: Annotated[int, Field(ge=0, alias="ground"), BeforeValidator(int)] = 0
    fly_balls: Annotated[int, Field(ge=0, alias="fly"), BeforeValidator(int)] = 0
    grounded_into_double_plays: Annotated[
        int, Field(ge=0, alias="gdp"), BeforeValidator(int)
    ] = 0
    hit_into_double_plays: Annotated[
        int, Field(ge=0, alias="hitdp"), BeforeValidator(int)
    ] = 0
    hit_into_triple_plays: Annotated[
        int, Field(ge=0, alias="hittp"), BeforeValidator(int)
    ] = 0
    hit_by_pitch: Annotated[int, Field(ge=0, alias="hbp"), BeforeValidator(int)] = 0
    kl: Annotated[int, Field(ge=0), BeforeValidator(int)] = (
        0  # i don't know what this is. strikeouts looking? called strikes?
    )
    strikeouts: Annotated[int, Field(ge=0, alias="so"), BeforeValidator(int)] = 0
    pickoffs: Annotated[int, Field(ge=0, alias="picked"), BeforeValidator(int)] = 0
    runs: Annotated[int, Field(ge=0, alias="r"), BeforeValidator(int)] = 0
    runs_batted_in: Annotated[int, Field(ge=0, alias="rbi"), BeforeValidator(int)] = 0
    stolen_bases: Annotated[int, Field(ge=0, alias="sb"), BeforeValidator(int)] = 0
    caught_stealings: Annotated[int, Field(ge=0, alias="cs"), BeforeValidator(int)] = 0
    sacrifice_flies: Annotated[int, Field(ge=0, alias="sf"), BeforeValidator(int)] = 0
    sacrifice_hits: Annotated[int, Field(ge=0, alias="sh"), BeforeValidator(int)] = 0


class TeamTotalsPitching(BaseModel):
    at_bats: Annotated[int, Field(ge=0, alias="ab"), BeforeValidator(int)] = 0
    innings_pitched: Annotated[
        float, Field(ge=0, alias="ip"), BeforeValidator(float)
    ] = 0.0
    pitches: Annotated[int, Field(ge=0), BeforeValidator(int)] = 0
    strikes: Annotated[int, Field(ge=0), BeforeValidator(int)] = 0
    wild_pitches: Annotated[int, Field(ge=0, alias="wp"), BeforeValidator(int)] = 0
    bf: Annotated[int, Field(ge=0), BeforeValidator(int)] = (
        0  # i don't know what this is. foul balls?
    )
    bk: Annotated[int, Field(ge=0), BeforeValidator(int)] = (
        0  # i don't know what this is.
    )
    bases_on_balls: Annotated[int, Field(ge=0, alias="bb"), BeforeValidator(int)] = 0
    intentional_bases_on_balls: Annotated[
        int, Field(ge=0, alias="ibb"), BeforeValidator(int)
    ] = 0
    hits_allowed: Annotated[int, Field(ge=0, alias="h"), BeforeValidator(int)] = 0
    doubles_allowed: Annotated[
        int, Field(ge=0, alias="double"), BeforeValidator(int)
    ] = 0
    triples_allowed: Annotated[
        int, Field(ge=0, alias="triple"), BeforeValidator(int)
    ] = 0
    home_runs_allowed: Annotated[int, Field(ge=0, alias="hr"), BeforeValidator(int)] = 0
    runs_allowed: Annotated[int, Field(ge=0, alias="r"), BeforeValidator(int)] = 0
    earned_runs_allowed: Annotated[
        int, Field(ge=0, alias="er"), BeforeValidator(int)
    ] = 0
    ground_balls: Annotated[int, Field(ge=0, alias="ground"), BeforeValidator(int)] = 0
    fly_balls: Annotated[int, Field(ge=0, alias="fly"), BeforeValidator(int)] = 0
    grounded_into_double_play: Annotated[
        int, Field(ge=0, alias="gdp"), BeforeValidator(int)
    ] = 0
    hit_by_pitch: Annotated[int, Field(ge=0, alias="hbp"), BeforeValidator(int)] = 0
    kl: Annotated[int, Field(ge=0), BeforeValidator(int)] = (
        0  # i don't know what this is. strikeouts looking? called strikes?
    )
    pickoffs: Annotated[int, Field(ge=0, alias="picked"), BeforeValidator(int)] = 0
    sacrifice_flies_allowed: Annotated[
        int, Field(ge=0, alias="sfa"), BeforeValidator(int)
    ] = 0
    sacrifice_hits_allowed: Annotated[
        int, Field(ge=0, alias="sha"), BeforeValidator(int)
    ] = 0
    strikeouts: Annotated[int, Field(ge=0, alias="so"), BeforeValidator(int)] = 0


class TeamTotalsFielding(BaseModel):
    assists: Annotated[int, Field(ge=0, alias="a"), BeforeValidator(int)] = 0
    catchers_interference: Annotated[
        int, Field(ge=0, alias="ci"), BeforeValidator(int)
    ] = 0
    errors: Annotated[int, Field(ge=0, alias="e"), BeforeValidator(int)] = 0
    passed_balls: Annotated[int, Field(ge=0, alias="pb"), BeforeValidator(int)] = 0
    putouts: Annotated[int, Field(ge=0, alias="po"), BeforeValidator(int)] = 0
    stolen_bases_allowed: Annotated[
        int, Field(ge=0, alias="sba"), BeforeValidator(int)
    ] = 0


class TeamTotals(BaseModel):
    runs: Annotated[int, Field(ge=0)] = 0
    hits: Annotated[int, Field(ge=0)] = 0
    errors: Annotated[int, Field(ge=0)] = 0
    left_on_base: Annotated[int, Field(ge=0)] = 0
    batting: TeamTotalsBatting
    pitching: TeamTotalsPitching
    fielding: TeamTotalsFielding


class PlayerPosition(str, Enum):
    PITCHER = "p"
    CATCHER = "c"
    FIRST_BASE = "1b"
    SECOND_BASE = "2b"
    THIRD_BASE = "3b"
    SHORTSTOP = "ss"
    LEFT_FIELD = "lf"
    CENTER_FIELD = "cf"
    RIGHT_FIELD = "rf"
    DESIGNATED_HITTER = "dh"
    PINCH_HITTER = "ph"

    @staticmethod
    def before_validator(value: Any) -> set[PlayerPosition] | None:
        if not isinstance(value, str):
            raise TypeError("Player position must be a string")
        if not value:
            return None

        position_re = "|".join(map(re.escape, PlayerPosition.__members__.values()))
        full_re = re.compile(f"^{position_re}(/{position_re})*$")
        if not full_re.match(value):
            raise ValueError(
                "Player position must be in the format of <position>(/<position>)*"
            )
        positions = set()
        for position in value.split("/"):
            positions.add(PlayerPosition(position))
        return positions


class Hand(str, Enum):
    LEFT = "L"
    RIGHT = "R"
    BOTH = "B"


class PlayerHitting(BaseModel):
    at_bats: Annotated[int, Field(ge=0, alias="ab"), BeforeValidator(int)] = 0
    runs: Annotated[int, Field(ge=0, alias="r"), BeforeValidator(int)] = 0
    runs_batted_in: Annotated[int, Field(ge=0, alias="rbi"), BeforeValidator(int)] = 0
    hits: Annotated[int, Field(ge=0, alias="h"), BeforeValidator(int)] = 0
    bases_on_balls: Annotated[int, Field(ge=0, alias="bb"), BeforeValidator(int)] = 0
    fly_balls: Annotated[int, Field(ge=0, alias="fly"), BeforeValidator(int)] = 0
    ground_balls: Annotated[int, Field(ge=0, alias="ground"), BeforeValidator(int)] = 0
    hit_into_double_plays: Annotated[
        int, Field(ge=0, alias="hitdp"), BeforeValidator(int)
    ] = 0
    on_base_percentage: (
        Annotated[float, Field(alias="obp"), BeforeValidator(float)] | None
    ) = None
    slugging_percentage: (
        Annotated[float, Field(alias="slg"), BeforeValidator(float)] | None
    ) = None
    on_base_plus_slugging: (
        Annotated[float, Field(alias="ops"), BeforeValidator(float)] | None
    ) = None


class PlayerFielding(BaseModel):
    assists: Annotated[int, Field(ge=0, alias="a"), BeforeValidator(int)] = 0
    errors: Annotated[int, Field(ge=0, alias="e"), BeforeValidator(int)] = 0
    putouts: Annotated[int, Field(ge=0, alias="po"), BeforeValidator(int)] = 0


def str_or_none(value: str) -> str | None:
    return value or None


class Player(BaseModel):
    id: Annotated[str, AfterValidator(str_or_none)] | None = None
    profile_url: Annotated[str, AfterValidator(str_or_none)] | None = None
    name: str
    short_name: str
    uniform: int
    positions: (
        Annotated[
            set[PlayerPosition],
            Field(alias="position"),
            BeforeValidator(PlayerPosition.before_validator),
        ]
        | None
    ) = None
    spot: Annotated[int, Field(ge=0)]
    bats: Hand
    throws: Hand
    hitting: PlayerHitting | None = None
    fielding: PlayerFielding | None = None


class Starter(BaseModel):
    name: str
    uniform: int
    position: PlayerPosition
    spot: Annotated[int, Field(ge=1)]


class Team(BaseModel):
    side: Side
    id: str
    team_url: str
    code: str
    name: str
    record: Annotated[TeamRecord, BeforeValidator(TeamRecord.before_validator)]
    line: list[LineScoreInning]
    totals: TeamTotals
    players: list[Player]
    starters: list[Starter]
