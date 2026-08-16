from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Annotated
from .team import PlayerPosition

import re


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
    PASSED_BALL = "passed_ball"
    HIT_BY_PITCH = "hit_by_pitch"
    # the API uses the UNKNOWN variant for the below events, but it's more helfpul to have these custom variants; these are set in `Play.fix`; if the API introduces its own version of any of these variants, they will need to be updated
    REACH_ON_ERROR = "reach_on_error"
    BALK = "balk"
    SUBSTITUTION = "substitution"
    FAILED_PICKOFF_ATTEMPT = "failed_pickoff_attempt"
    GHOST_RUNNER_PLACEMENT = "ghost_runner_placement"

    @classmethod
    def _missing_(cls, value) -> EventType:
        return EventType.WPYBL_UNKNOWN


class PitchEventCode(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    HIT_BY_PITCH = "H"
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
    CALLED_STRIKE = "called_strike"  # the API uses the UNKNOWN variant for this event, but it's more helpful to have this custom variant; this is set in `Play.fix`; if the API introduces its own version of this, then this will need to be updated
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
    batter_id: str | None = None  # this is set in `Game.add_player_ids_to_plays`
    batter_name: str
    pitcher_id: str | None = None  # this is set in `Game.add_player_ids_to_plays`
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

    @model_validator(mode="after")
    def fix(self) -> Play:
        # fix UNKNOWN events
        if self.event_type == EventType.UNKNOWN:
            narrative = self.narrative.lower()
            if "on an error" in narrative or re.search(
                "advanced to (second|third|home) on the throw", narrative
            ):
                self.event_type = EventType.REACH_ON_ERROR
            elif "on a balk" in narrative:
                self.event_type = EventType.BALK
            elif (
                re.search(f"to {PlayerPosition.position_re()}", narrative)
                or "pinch hit for" in narrative
                or "pinch ran for" in narrative
            ):
                self.event_type = EventType.SUBSTITUTION
            elif "failed pickoff attempt" in narrative:
                self.event_type = EventType.FAILED_PICKOFF_ATTEMPT
            elif "placed on second" in narrative:
                self.event_type = EventType.GHOST_RUNNER_PLACEMENT

        # fix UNKNOWN pitch events
        if self.pitch_events is not None:
            for pitch in self.pitch_events:
                if (
                    pitch.type == PitchEventType.UNKNOWN
                    and pitch.code == PitchEventCode.CALLED_STRIKE
                ):
                    pitch.type = PitchEventType.CALLED_STRIKE

        # fix `runs_scored` values
        # the API does not count the RBI scored by the batter on a home run, so we need to extract it from the narrative;
        # we could just `self.runs_scored += 1` on homers, but that will break if the API is fixed in the future. this method is more robust
        if ", RBI" in self.narrative:
            self.runs_scored = 1
        elif (m := re.search(r"(1|2|3|4) RBI", self.narrative)) is not None:
            self.runs_scored = int(m.group(1))

        return self

    def to_csv_row(self) -> dict[str, str | int | float | None]:
        return {
            "sequence": self.sequence,
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
