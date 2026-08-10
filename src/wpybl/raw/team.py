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
    at_bats: Annotated[int, Field(ge=0, alias="ab")] = 0
    bases_on_balls: Annotated[int, Field(ge=0, alias="bb")] = 0
    intentional_bases_on_balls: Annotated[int, Field(ge=0, alias="ibb")] = 0
    hits: Annotated[int, Field(ge=0, alias="h")] = 0
    doubles: Annotated[int, Field(ge=0, alias="double")] = 0
    triples: Annotated[int, Field(ge=0, alias="triple")] = 0
    home_runs: Annotated[int, Field(ge=0, alias="hr")] = 0
    ground_balls: Annotated[int, Field(ge=0, alias="ground")] = 0
    fly_balls: Annotated[int, Field(ge=0, alias="fly")] = 0
    grounded_into_double_plays: Annotated[int, Field(ge=0, alias="gdp")] = 0
    hit_into_double_plays: Annotated[int, Field(ge=0, alias="hitdp")] = 0
    hit_into_triple_plays: Annotated[int, Field(ge=0, alias="hittp")] = 0
    hit_by_pitch: Annotated[int, Field(ge=0, alias="hbp")] = 0
    kl: Annotated[int, Field(ge=0)] = (
        0  # i don't know what this is. strikeouts looking? called strikes?
    )
    strikeouts: Annotated[int, Field(ge=0, alias="so")] = 0
    pickoffs: Annotated[int, Field(ge=0, alias="picked")] = 0
    runs: Annotated[int, Field(ge=0, alias="r")] = 0
    runs_batted_in: Annotated[int, Field(ge=0, alias="rbi")] = 0
    stolen_bases: Annotated[int, Field(ge=0, alias="sb")] = 0
    cs: Annotated[int, Field(ge=0)] = (
        0  # i assume this is either called strikes or caught stealings
    )
    sacrifice_flies: Annotated[int, Field(ge=0, alias="sf")] = 0
    sacrifice_hits: Annotated[int, Field(ge=0, alias="sh")] = 0


class TeamTotalsPitching(BaseModel):
    at_bats: Annotated[int, Field(ge=0, alias="ab")] = 0
    innings_pitched: Annotated[float, Field(ge=0, alias="ip")] = 0.0
    pitches: Annotated[int, Field(ge=0)] = 0
    strikes: Annotated[int, Field(ge=0)] = 0
    wild_pitches: Annotated[int, Field(ge=0, alias="wp")] = 0
    bf: Annotated[int, Field(ge=0)] = 0  # i don't know what this is. foul balls?
    bk: Annotated[int, Field(ge=0)] = 0  # i don't know what this is
    bases_on_balls: Annotated[int, Field(ge=0, alias="bb")] = 0
    intentional_bases_on_balls: Annotated[int, Field(ge=0, alias="ibb")] = 0
    hits_allowed: Annotated[int, Field(ge=0, alias="h")] = 0
    doubles_allowed: Annotated[int, Field(ge=0, alias="double")] = 0
    triples_allowed: Annotated[int, Field(ge=0, alias="triple")] = 0
    home_runs_allowed: Annotated[int, Field(ge=0, alias="hr")] = 0
    runs_allowed: Annotated[int, Field(ge=0, alias="r")] = 0
    earned_runs_allowed: Annotated[int, Field(ge=0, alias="er")] = 0
    ground_balls: Annotated[int, Field(ge=0, alias="ground")] = 0
    fly_balls: Annotated[int, Field(ge=0, alias="fly")] = 0
    grounded_into_double_play: Annotated[int, Field(ge=0, alias="gdp")] = 0
    hit_by_pitch: Annotated[int, Field(ge=0, alias="hbp")] = 0
    kl: Annotated[int, Field(ge=0)] = (
        0  # i don't know what this is. strikeouts looking? called strikes?
    )
    pickoffs: Annotated[int, Field(ge=0, alias="picked")] = 0
    sacrifice_flies_allowed: Annotated[int, Field(ge=0, alias="sfa")] = 0
    sacrifice_hits_allowed: Annotated[int, Field(ge=0, alias="sha")] = 0
    strikeouts: Annotated[int, Field(ge=0, alias="so")] = 0


class TeamTotalsFielding(BaseModel):
    assists: Annotated[int, Field(ge=0, alias="a")] = 0
    catchers_interference: Annotated[int, Field(ge=0, alias="ci")] = 0
    errors: Annotated[int, Field(ge=0, alias="e")] = 0
    passed_balls: Annotated[int, Field(ge=0, alias="pb")] = 0
    putouts: Annotated[int, Field(ge=0, alias="po")] = 0
    stolen_bases_allowed: Annotated[int, Field(ge=0, alias="sba")] = 0
    indp: Annotated[int, Field(ge=0, alias="indp")] = 0  # i don't know what this is
    csb: Annotated[int, Field(ge=0, alias="csb")] = (
        0  # i don't know what this is either
    )


class TeamTotals(BaseModel):
    runs: Annotated[int, Field(ge=0)] = 0
    hits: Annotated[int, Field(ge=0)] = 0
    errors: Annotated[int, Field(ge=0)] = 0
    left_on_base: Annotated[int, Field(ge=0)] = 0
    batting: TeamTotalsBatting
    pitching: TeamTotalsPitching
    fielding: TeamTotalsFielding


class PlayerPosition(str, Enum):
    UNKNOWN = "unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
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

    @classmethod
    def _missing_(cls, value) -> PlayerPosition:
        return PlayerPosition.UNKNOWN

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
    UNKNOWN = "unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    LEFT = "L"
    RIGHT = "R"
    BOTH = "B"

    @classmethod
    def _missing_(cls, value) -> Hand:
        return Hand.UNKNOWN


class PlayerHitting(BaseModel):
    at_bats: Annotated[int, Field(ge=0, alias="ab")] = 0
    runs: Annotated[int, Field(ge=0, alias="r")] = 0
    runs_batted_in: Annotated[int, Field(ge=0, alias="rbi")] = 0
    hits: Annotated[int, Field(ge=0, alias="h")] = 0
    doubles: Annotated[int, Field(ge=0, alias="double")] = 0
    triples: Annotated[int, Field(ge=0, alias="triple")] = 0
    home_runs: Annotated[int, Field(ge=0, alias="hr")] = 0
    bases_on_balls: Annotated[int, Field(ge=0, alias="bb")] = 0
    ground_balls: Annotated[int, Field(ge=0, alias="ground")] = 0
    fly_balls: Annotated[int, Field(ge=0, alias="fly")] = 0
    hit_into_double_plays: Annotated[int, Field(ge=0, alias="hitdp")] = 0
    kl: Annotated[int, Field(ge=0)] = (
        0  # i don't know what this is. strikeouts looking? called strikes?
    )
    strikeouts: Annotated[int, Field(ge=0, alias="so")] = 0
    hit_by_pitches: Annotated[int, Field(ge=0, alias="hbp")] = 0
    stolen_bases: Annotated[int, Field(ge=0, alias="sb")] = 0
    sacrifice_flies: Annotated[int, Field(ge=0, alias="sf")] = 0
    pickoffs: Annotated[int, Field(ge=0, alias="picked")] = 0
    cs: Annotated[int, Field(ge=0)] = (
        0  # i assume this is either called strikes or caught stealings
    )
    on_base_percentage: Annotated[float | None, Field(alias="obp")] = None
    slugging_percentage: Annotated[float | None, Field(alias="slg")] = None
    on_base_plus_slugging: Annotated[float | None, Field(alias="ops")] = None


class PlayerPitching(BaseModel):
    at_bats: Annotated[int, Field(ge=0, alias="ab")] = 0
    innings_pitched: Annotated[float, Field(ge=0, alias="ip")] = 0.0
    pitches: Annotated[int, Field(ge=0)] = 0
    strikes: Annotated[int, Field(ge=0)] = 0
    appear: Annotated[int, Field(ge=0)] = 0
    bases_on_balls: Annotated[int, Field(ge=0, alias="bb")] = 0
    bf: Annotated[int, Field(ge=0)] = 0  # i don't know what this is. foul balls?
    bk: Annotated[int, Field(ge=0)] = 0  # i don't know what this is
    hits_allowed: Annotated[int, Field(ge=0, alias="h")] = 0
    doubles_allowed: Annotated[int, Field(ge=0, alias="double")] = 0
    triples_allowed: Annotated[int, Field(ge=0, alias="triple")] = 0
    home_runs_allowed: Annotated[int, Field(ge=0, alias="hr")] = 0
    runs_allowed: Annotated[int, Field(ge=0, alias="r")] = 0
    earned_runs_allowed: Annotated[int, Field(ge=0, alias="er")] = 0
    ground_balls: Annotated[int, Field(ge=0, alias="ground")] = 0
    fly_balls: Annotated[int, Field(ge=0, alias="fly")] = 0
    gs: Annotated[int, Field(ge=0)] = 0  # i don't know what this is
    hit_by_pitches: Annotated[int, Field(ge=0, alias="hbp")] = 0
    kl: Annotated[int, Field(ge=0)] = (
        0  # i don't know what this is. strikeouts looking? called strikes?
    )
    wild_pitches: Annotated[int, Field(ge=0, alias="wp")] = 0
    strikeouts: Annotated[int, Field(ge=0, alias="so")] = 0
    sacrifice_flies_allowed: Annotated[int, Field(ge=0, alias="sfa")] = 0
    pickoffs: Annotated[int, Field(ge=0, alias="picked")] = 0
    win: str | None = None  # i don't know what this is
    loss: str | None = None  # i don't know what this is either lol
    whip: Annotated[float, Field(ge=0, alias="whip")] = 0.0


class PlayerFielding(BaseModel):
    assists: Annotated[int, Field(ge=0, alias="a")] = 0
    errors: Annotated[int, Field(ge=0, alias="e")] = 0
    putouts: Annotated[int, Field(ge=0, alias="po")] = 0
    stolen_bases_allowed: Annotated[int, Field(ge=0, alias="sba")] = 0
    indp: Annotated[int, Field(ge=0, alias="indp")] = 0  # i don't know what this is
    csb: Annotated[int, Field(ge=0, alias="csb")] = 0  # i don't know what this is


def str_or_none(value: str) -> str | None:
    return value or None


class Player(BaseModel):
    id: Annotated[str | None, AfterValidator(str_or_none)] = None
    profile_url: Annotated[str | None, AfterValidator(str_or_none)] = None
    name: str
    short_name: str
    uniform: int
    positions: Annotated[
        set[PlayerPosition] | None,
        Field(alias="position"),
        BeforeValidator(PlayerPosition.before_validator),
    ] = None
    spot: int
    bats: Hand
    throws: Hand
    hitting: PlayerHitting | None = None
    pitching: PlayerPitching | None = None
    fielding: PlayerFielding | None = None


class Starter(BaseModel):
    name: str
    uniform: int
    position: PlayerPosition
    spot: int


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

    def has_player(self, player_name: str) -> bool:
        return any(player.name == player_name for player in self.players)

    def get_player(self, player_name: str) -> Player | None:
        for player in self.players:
            if player.name == player_name:
                return player
