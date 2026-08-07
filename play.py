from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated


class Half(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"


class EventType(str, Enum):
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


class PitchEventCode(str, Enum):
    HIT = "H"
    CALLED_STRIKE = "K"
    SWINGING_STRIKE = "S"
    BALL = "B"
    PITCHOUT = "P"
    FOUL = "F"


class PitchEventType(str, Enum):
    UNKNOWN = "unknown"
    SWINGING_STRIKE = "swinging_strike"
    FOUL = "foul"
    PITCHOUT = "pitchout"
    BALL = "ball"
    HIT_BY_PITCH = "hit_by_pitch"


class PitchEvent(BaseModel):
    sequence: Annotated[int, Field(ge=1)]
    code: PitchEventCode
    type: PitchEventType
    description: str


class Play(BaseModel):
    inning: Annotated[int, Field(ge=1)]
    half: Half
    team_id: str
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
    pitch_sequence: str
    pitch_events: list[PitchEvent] | None = None
    fouls: Annotated[int, Field(ge=0)]
    balls: Annotated[int, Field(ge=0, le=4)]
    strikes: Annotated[int, Field(ge=0, le=3)]
