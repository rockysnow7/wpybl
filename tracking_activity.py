from __future__ import annotations
from datetime import datetime
from enum import Enum
from play import Half
from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from typing import Annotated, Any


class EventType(str, Enum):
    REST_RECONCILIATION = "rest_reconciliation"


class Kind(str, Enum):
    PITCH = "pitch"
    HIT = "hit"


class PitchType(str, Enum):
    UNDEFINED = "Undefined"
    SLIDER = "Slider"
    CHANGEUP = "ChangeUp"
    FASTBALL = "Fastball"
    SPLITTER = "Splitter"
    FOUR_SEAM_FASTBALL = "FourSeamFastBall"
    CURVEBALL = "Curveball"


class HitType(str, Enum):
    UNDEFINED = "Undefined"
    GROUND_BALL = "GroundBall"
    LINE_DRIVE = "LineDrive"
    FLY_BALL = "FlyBall"
    POPUP = "Popup"


class SpeedUnit(str, Enum):
    MPH = "mph"


class DistanceUnit(str, Enum):
    FEET = "feet"


class TrackingActivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activity_id: str | None = None
    game_id: str
    provider: str
    session_id: str
    play_id: str
    event_type: EventType
    kind: Kind
    sequence: Annotated[int, Field(ge=1)]
    occurred_at: datetime
    inning: Annotated[int | None, Field(ge=1)] = None
    half: Half | None = None
    pitcher_id: str | None = None
    provider_pitcher_id: str | None = None
    pitcher_name: str | None = None
    batter_id: str | None = None
    provider_batter_id: str | None = None
    batter_name: str | None = None
    pitch_type: PitchType | None = None
    hit_type: HitType | None = None
    release_speed: Annotated[float, Field(ge=0)]
    exit_speed: Annotated[float | None, Field(ge=0)] = None
    speed_unit: SpeedUnit
    spin_rate_rpm: Annotated[float, Field(ge=0)]
    extension: Annotated[float | None, Field(ge=0)] = None
    distance: Annotated[float | None, Field(ge=0)] = None
    distance_unit: DistanceUnit
    launch_angle_deg: float | None = None
    horizontal_angle_deg: float | None = None
    vertical_break: float
    horizontal_break: float
    plate_location_height: float
    plate_location_side: float
    created_at: datetime
    updated_at: datetime
