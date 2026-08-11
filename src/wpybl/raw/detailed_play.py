# The classes in this file are not parsed directly from the API, but instead
# combine data from `.play.Play` and `.tracking_activity.TrackingActivity`.
# They are the only classes in `.raw` that are not parsed directly from the API.

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .play import EventType, Half, PitchEventType
from .tracking_activity import DistanceUnit, HitType, PitchType, SpeedUnit


@dataclass
class Pitch:
    pitch_type: PitchType | None
    release_speed: float
    speed_unit: SpeedUnit
    spin_rate_rpm: float
    extension: float | None
    distance_unit: DistanceUnit
    vertical_break: float
    horizontal_break: float
    plate_location_height: float
    plate_location_side: float
    pitch_event_type: PitchEventType
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


@dataclass
class Hit:
    hit_type: HitType
    exit_speed: float
    distance: float
    launch_angle_deg: float
    horizontal_angle_deg: float
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


@dataclass
class DetailedPlay:
    """Combines play-by-play data with tracking activity data."""

    inning: int
    half: Half
    batting_team_id: str
    sequence: int
    batter_name: str
    pitcher_name: str
    outs: int
    first_base: str
    second_base: str
    third_base: str
    bases_occupied: list[int]
    bases_loaded: bool
    narrative: str
    event_type: EventType
    is_hit: bool
    is_scoring_play: bool
    runs_scored: int
    final_fouls: int
    final_balls: int
    final_strikes: int
    pitches: list[Pitch]
    hit: Hit | None = None
