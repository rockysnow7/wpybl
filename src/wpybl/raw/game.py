from __future__ import annotations
from datetime import datetime
from .detailed_play import DetailedPlay, Hit, Pitch
from enum import Enum
from .play import Half, Play
from pydantic import BaseModel, Field, model_validator
from .team import Team, Player
from .tracking_activity import TrackingActivity
from typing import Annotated

import pandas as pd


class GameStatus(str, Enum):
    WPYBL_UNKNOWN = "wpybl_unknown"
    """A variant indicating that the raw JSON value did not match any known variants, and that this enum needs to be updated accordingly."""
    FINAL = "Final"
    UPCOMING = "Upcoming"

    @classmethod
    def _missing_(cls, value) -> GameStatus:
        if isinstance(value, str):
            if value.lower().startswith(
                "final"
            ):  # extra-innings games have the format "Final - <number> innings"
                return GameStatus.FINAL
            if value.lower().startswith("upcoming"):
                return GameStatus.UPCOMING
        return GameStatus.WPYBL_UNKNOWN


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
    tracking_activities: Annotated[
        list[TrackingActivity] | None, Field(alias="tracking_activity")
    ] = None

    def get_player_id(self, player_name: str) -> str | None:
        for team in self.teams:
            for player in team.players:
                if player.name == player_name:
                    return player.id

    @model_validator(mode="after")
    def add_player_ids_to_plays(self) -> Game:
        player_ids = {}

        for play in self.plays:
            if play.batter_name not in player_ids:
                player_ids[play.batter_name] = self.get_player_id(play.batter_name)
            play.batter_id = player_ids[play.batter_name]

            if play.pitcher_name not in player_ids:
                player_ids[play.pitcher_name] = self.get_player_id(play.pitcher_name)
            play.pitcher_id = player_ids[play.pitcher_name]

        return self

    @staticmethod
    def from_json(json: dict) -> Game:
        if "boxscore" not in json:
            raise ValueError("JSON does not contain a boxscore")
        return Game.model_validate(json["boxscore"])

    def get_team(self, team_name: str) -> Team | None:
        for team in self.teams:
            if team.name == team_name:
                return team

    def get_player(self, player_name: str) -> Player | None:
        for team in self.teams:
            for player in team.players:
                if player.name == player_name:
                    return player

    def __filter_tracking_activities_for_detailed_plays(
        self,
        inning: int,
        half: Half,
        pitcher_id: str,
        batter_id: str,
    ) -> list[TrackingActivity]:
        if not self.tracking_activities:
            return []

        return [
            ta
            for ta in self.tracking_activities
            if ta.inning == inning
            and ta.half == half
            and ta.pitcher_id == pitcher_id
            and ta.batter_id == batter_id
        ]

    def detailed_plays(self) -> list[DetailedPlay]:
        """
        Returns a list of `DetailedPlay` objects, which combine play-by-play data with tracking activity data.
        The returned list only includes plays that involve the pitcher pitching to the batter, and possibly the batter hitting the ball.
        The returned list will not necessarily include every play of the game, as some plays may not have tracking activity data.
        """

        if self.tracking_activities is None:
            return []

        detailed_plays = []
        for play in self.plays:
            if (
                play.inning is None
                or play.half is None
                or play.pitcher_id is None
                or play.batter_id is None
            ):
                continue
            if not play.pitch_events:
                continue

            relevant_tracking_activities = (
                self.__filter_tracking_activities_for_detailed_plays(
                    play.inning,
                    play.half,
                    play.pitcher_id,
                    play.batter_id,
                )
            )
            if not relevant_tracking_activities:
                continue

            ta_hits = [ta for ta in relevant_tracking_activities if ta.includes_hit()]
            if len(ta_hits) == 1:
                ta = ta_hits[0]

                assert ta.hit_type
                assert ta.exit_speed
                assert ta.distance
                assert ta.launch_angle_deg
                assert ta.horizontal_angle_deg

                hit = Hit(
                    hit_type=ta.hit_type,
                    exit_speed=ta.exit_speed,
                    distance=ta.distance,
                    launch_angle_deg=ta.launch_angle_deg,
                    horizontal_angle_deg=ta.horizontal_angle_deg,
                    occurred_at=ta.occurred_at,
                    created_at=ta.created_at,
                    updated_at=ta.updated_at,
                )
            elif len(ta_hits) == 0:
                hit = None
            else:
                continue

            if len(relevant_tracking_activities) != len(play.pitch_events):
                continue

            pitches = []
            relevant_tracking_activities = sorted(
                relevant_tracking_activities, key=lambda x: x.occurred_at
            )
            for pitch_event, ta in zip(play.pitch_events, relevant_tracking_activities):
                pitch = Pitch(
                    pitch_type=ta.pitch_type,
                    release_speed=ta.release_speed,
                    speed_unit=ta.speed_unit,
                    spin_rate_rpm=ta.spin_rate_rpm,
                    extension=ta.extension,
                    distance_unit=ta.distance_unit,
                    vertical_break=ta.vertical_break,
                    horizontal_break=ta.horizontal_break,
                    plate_location_height=ta.plate_location_height,
                    plate_location_side=ta.plate_location_side,
                    pitch_event_type=pitch_event.type,
                    occurred_at=ta.occurred_at,
                    created_at=ta.created_at,
                    updated_at=ta.updated_at,
                )
                pitches.append(pitch)

            detailed_play = DetailedPlay(
                inning=play.inning,
                half=play.half,
                batting_team_id=play.batting_team_id,
                sequence=play.sequence,
                batter_name=play.batter_name,
                pitcher_name=play.pitcher_name,
                outs=play.outs,
                first_base=play.first_base,
                second_base=play.second_base,
                third_base=play.third_base,
                bases_occupied=play.bases_occupied,
                bases_loaded=play.bases_loaded,
                narrative=play.narrative,
                event_type=play.event_type,
                is_hit=play.is_hit,
                is_scoring_play=play.is_scoring_play,
                runs_scored=play.runs_scored,
                final_fouls=play.final_fouls,
                final_balls=play.final_balls,
                final_strikes=play.final_strikes,
                pitches=pitches,
                hit=hit,
            )
            detailed_plays.append(detailed_play)

        return detailed_plays

    def plays_to_df(self, *, save_to_path: str | None = None) -> pd.DataFrame:
        """
        Converts the game's play-by-play records to a pandas DataFrame and optionally saves it to a CSV file at the specified path.

        Args:
            save_to_path (str, optional): If specified, the DataFrame will be saved to the specified path as a CSV file. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing the game's plays.
        """

        rows = [play.to_csv_row() for play in self.plays]
        df = pd.DataFrame(rows).set_index("sequence")
        if save_to_path is not None:
            df.to_csv(save_to_path)
        return df
