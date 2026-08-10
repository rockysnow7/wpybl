from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated


class Half(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"


class EventType(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    UNKNOWN = "unknown"
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    HOME_RUN = "home_run"
    SACRIFICE = "sacrifice"
    OUT = "out"
    GROUNDOUT = "groundout"
    LINEOUT = "lineout"
    FLYOUT = "flyout"
    POPUP = "popup"
    FOUL_OUT = "foul_out"
    FIELDERS_CHOICE = "fielders_choice"
    STRIKEOUT = "strikeout"
    WALK = "walk"
    STOLEN_BASE = "stolen_base"
    CAUGHT_STEALING = "caught_stealing"
    WILD_PITCH = "wild_pitch"
    HIT_BY_PITCH = "hit_by_pitch"

    @classmethod
    def _missing_(cls, value) -> EventType:
        return EventType.WPYBL_UNKNOWN


class PitchEventCode(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    HIT = "H"
    CALLED_STRIKE = "K"
    SWINGING_STRIKE = "S"
    BALL = "B"
    PITCHOUT = "P"
    FOUL = "F"

    @classmethod
    def _missing_(cls, value) -> PitchEventCode:
        return PitchEventCode.WPYBL_UNKNOWN


class PitchEventType(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    UNKNOWN = "unknown"
    SWINGING_STRIKE = "swinging_strike"
    FOUL = "foul"
    PITCHOUT = "pitchout"
    BALL = "ball"
    HIT_BY_PITCH = "hit_by_pitch"

    @classmethod
    def _missing_(cls, value) -> PitchEventType:
        return PitchEventType.WPYBL_UNKNOWN


class PitchEvent(BaseModel):
    sequence: Annotated[int, Field(ge=1)]
    code: PitchEventCode
    type: PitchEventType
    description: str


class Play(BaseModel):
    inning: Annotated[int, Field(ge=1)]
    half: Half
    batting_team_id: Annotated[str, Field(alias="team_id")]
    sequence: Annotated[int, Field(ge=1)]
    batter_name: str
    pitcher_name: str
    outs: Annotated[int, Field(ge=0, le=3)]
    first_base: str
    second_base: str
    third_base: str
    bases_occupied: list[Annotated[int, Field(ge=1, le=3)]]
    bases_loaded: bool
    narrative: str
    event_type: EventType
    is_hit: bool
    is_scoring_play: bool = False
    runs_scored: Annotated[int, Field(ge=0, le=4)] = 0
    pitch_sequence: str
    pitch_events: list[PitchEvent] | None = None
    final_fouls: Annotated[int, Field(ge=0, alias="fouls")]
    final_balls: Annotated[int, Field(ge=0, le=4, alias="balls")]
    final_strikes: Annotated[int, Field(ge=0, le=3, alias="strikes")]

    def to_csv_row(self) -> dict[str, str | int | float]:
        return {
            "sequence": self.sequence,
            "inning": self.inning,
            "half": self.half.value,
            "outs": self.outs,
            "batting_team_id": self.batting_team_id,
            "batter_name": self.batter_name,
            "pitcher_name": self.pitcher_name,
            "first_base": self.first_base,
            "second_base": self.second_base,
            "third_base": self.third_base,
            "pitch_sequence": self.pitch_sequence,
            "final_balls": self.final_balls,
            "final_strikes": self.final_strikes,
            "final_fouls": self.final_fouls,
            "event_type": self.event_type.value,
            "is_hit": self.is_hit,
            "is_scoring_play": self.is_scoring_play,
            "runs_scored": self.runs_scored,
            "narrative": self.narrative,
        }
