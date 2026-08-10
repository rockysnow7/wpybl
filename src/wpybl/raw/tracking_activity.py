from __future__ import annotations
from datetime import datetime
from enum import Enum
from .play import Half
from pydantic import BaseModel, Field
from typing import Annotated


class EventType(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    REST_RECONCILIATION = "rest_reconciliation"

    @classmethod
    def _missing_(cls, value) -> EventType:
        return EventType.WPYBL_UNKNOWN


class Kind(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    PITCH = "pitch"
    HIT = "hit"

    @classmethod
    def _missing_(cls, value) -> Kind:
        return Kind.WPYBL_UNKNOWN


class PitchType(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    UNDEFINED = "Undefined"
    SLIDER = "Slider"
    CHANGEUP = "ChangeUp"
    FASTBALL = "Fastball"
    SPLITTER = "Splitter"
    FOUR_SEAM_FASTBALL = "FourSeamFastBall"
    CURVEBALL = "Curveball"

    @classmethod
    def _missing_(cls, value) -> PitchType:
        return PitchType.WPYBL_UNKNOWN


class HitType(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    UNDEFINED = "Undefined"
    GROUND_BALL = "GroundBall"
    LINE_DRIVE = "LineDrive"
    FLY_BALL = "FlyBall"
    POPUP = "Popup"

    @classmethod
    def _missing_(cls, value) -> HitType:
        return HitType.WPYBL_UNKNOWN


class SpeedUnit(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    MPH = "mph"

    @classmethod
    def _missing_(cls, value) -> SpeedUnit:
        return SpeedUnit.WPYBL_UNKNOWN


class DistanceUnit(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    FEET = "feet"

    @classmethod
    def _missing_(cls, value) -> DistanceUnit:
        return DistanceUnit.WPYBL_UNKNOWN


class TrackingActivity(BaseModel):
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
