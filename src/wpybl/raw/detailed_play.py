# The classes in this file are not parsed directly from the API, but instead
# combine data from `.play.Play` and `.tracking_activity.TrackingActivity`.
# They are the only classes in `.raw` that are not parsed directly from the API.

from __future__ import annotations
from copy import deepcopy
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

    def to_csv_row(self) -> dict[str, str | float | datetime | None]:
        return {
            "pitch_type": self.pitch_type.value if self.pitch_type else None,
            "pitch_release_speed": self.release_speed,
            "pitch_speed_unit": self.speed_unit.value if self.speed_unit else None,
            "pitch_spin_rate_rpm": self.spin_rate_rpm,
            "pitch_extension": self.extension,
            "pitch_distance_unit": self.distance_unit.value,
            "pitch_vertical_break": self.vertical_break,
            "pitch_horizontal_break": self.horizontal_break,
            "pitch_plate_location_height": self.plate_location_height,
            "pitch_plate_location_side": self.plate_location_side,
            "pitch_event_type": self.pitch_event_type.value,
            "pitch_occurred_at": self.occurred_at,
            "pitch_created_at": self.created_at,
            "pitch_updated_at": self.updated_at,
        }


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

    def to_csv_row(self) -> dict[str, str | float | datetime | None]:
        return {
            "hit_type": self.hit_type.value,
            "hit_exit_speed": self.exit_speed,
            "hit_distance": self.distance,
            "hit_launch_angle_deg": self.launch_angle_deg,
            "hit_horizontal_angle_deg": self.horizontal_angle_deg,
            "hit_occurred_at": self.occurred_at,
            "hit_created_at": self.created_at,
            "hit_updated_at": self.updated_at,
        }

    @staticmethod
    def empty_csv_row() -> dict[str, None]:
        return {
            "hit_type": None,
            "hit_exit_speed": None,
            "hit_distance": None,
            "hit_launch_angle_deg": None,
            "hit_horizontal_angle_deg": None,
            "hit_occurred_at": None,
            "hit_created_at": None,
            "hit_updated_at": None,
        }


@dataclass
class _PitchCount:
    balls: int
    strikes: int
    fouls: int

    def __init__(self, balls: int, strikes: int, fouls: int) -> None:
        self.balls = balls
        self.strikes = strikes
        self.fouls = fouls

    @staticmethod
    def empty() -> _PitchCount:
        return _PitchCount(0, 0, 0)

    def ball(self) -> _PitchCount:
        return _PitchCount(self.balls + 1, self.strikes, self.fouls)

    def strike(self) -> _PitchCount:
        return _PitchCount(self.balls, self.strikes + 1, self.fouls)

    def foul(self) -> _PitchCount:
        return _PitchCount(self.balls, min(2, self.strikes + 1), self.fouls + 1)


@dataclass
class DetailedPlay:
    """Combines play-by-play data with tracking activity data."""

    sequence: int
    inning: int
    half: Half
    outs: int
    batting_team_id: str
    batter_id: str
    batter_name: str
    pitcher_id: str
    pitcher_name: str
    first_base: str
    second_base: str
    third_base: str
    bases_occupied: list[int]
    bases_loaded: bool
    event_type: EventType
    is_hit: bool
    is_scoring_play: bool
    runs_scored: int
    final_balls: int
    final_strikes: int
    final_fouls: int
    narrative: str
    pitches: list[Pitch]
    hit: Hit | None = None

    def to_csv_rows(self) -> list[dict[str, str | int | float]]:
        rows = []
        count = _PitchCount.empty()
        for i, pitch in enumerate(self.pitches):
            if i == len(self.pitches) - 1:
                if self.hit:
                    hit_row = self.hit.to_csv_row()
                else:
                    hit_row = Hit.empty_csv_row()

                event_type = self.event_type.value
                is_hit = self.is_hit
                is_scoring_play = self.is_scoring_play
                runs_scored = self.runs_scored
                narrative = self.narrative

                post_count = _PitchCount(
                    self.final_balls,
                    self.final_strikes,
                    self.final_fouls,
                )
            else:
                hit_row = Hit.empty_csv_row()
                event_type = None
                is_hit = None
                is_scoring_play = None
                runs_scored = None
                narrative = None

                match pitch.pitch_event_type:
                    case PitchEventType.BALL | PitchEventType.PITCHOUT:
                        post_count = count.ball()
                    case PitchEventType.SWINGING_STRIKE | PitchEventType.CALLED_STRIKE:
                        post_count = count.strike()
                    case PitchEventType.FOUL:
                        post_count = count.foul()
                    case _:
                        post_count = deepcopy(count)

            row = {
                "sequence": self.sequence,
                "pitch_sequence": i + 1,
                "inning": self.inning,
                "half": self.half.value,
                "outs": self.outs,
                "batting_team_id": self.batting_team_id,
                "batter_id": self.batter_id,
                "batter_name": self.batter_name,
                "pitcher_id": self.pitcher_id,
                "pitcher_name": self.pitcher_name,
                "first_base": self.first_base,
                "second_base": self.second_base,
                "third_base": self.third_base,
                "bases_loaded": self.bases_loaded,
                "event_type": event_type,
                "is_hit": is_hit,
                "is_scoring_play": is_scoring_play,
                "runs_scored": runs_scored,
                "balls_pre": count.balls,
                "strikes_pre": count.strikes,
                "fouls_pre": count.fouls,
                "balls_post": post_count.balls,
                "strikes_post": post_count.strikes,
                "fouls_post": post_count.fouls,
                "narrative": narrative,
            }
            row |= pitch.to_csv_row()
            row |= hit_row
            rows.append(row)

            count = post_count
        return rows
