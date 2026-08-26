"""Functions to calculate batting statistics from game data."""

from ..data import GamesCollection
from ..raw.play import EventType
from ..stats.teams import players, standings
from ._woba_utils import (
    get_all_plays,
    calculate_re24,
    calculate_run_values_and_counts,
    calculate_league_woba,
    calculate_league_obp,
    calculate_woba_weights,
    calculate_woba,
)

import pandas as pd


def player_batting_counting_stats(
    player_name: str, games: GamesCollection
) -> pd.DataFrame:
    """
    Calculates batting counting statistics for a particular player over a collection of games.

    Args:
        player_name (str): The name of the player to calculate statistics for.
        games (GamesCollection): The collection of games to calculate statistics over.

    Returns:
        pd.DataFrame: A DataFrame containing the player's batting counting statistics.
    """

    df = {
        "games": 0,
        "at_bats": 0,
        "plate_appearances": 0,
        "hits": 0,
        "singles": 0,
        "doubles": 0,
        "triples": 0,
        "home_runs": 0,
        "strikeouts": 0,
        "bases_on_balls": 0,
        "hit_by_pitches": 0,
        "rbi": 0,
        "sacrifice_flies": 0,
    }

    for game in games:
        if any(play.batter_name == player_name for play in game.plays):
            df["games"] += 1
        else:
            continue

        for play in game.plays:
            if play.batter_name == player_name:
                match play.event_type:
                    case EventType.SINGLE:
                        df["at_bats"] += 1
                        df["plate_appearances"] += 1
                        df["singles"] += 1
                    case EventType.DOUBLE:
                        df["at_bats"] += 1
                        df["plate_appearances"] += 1
                        df["doubles"] += 1
                    case EventType.TRIPLE:
                        df["at_bats"] += 1
                        df["plate_appearances"] += 1
                        df["triples"] += 1
                    case EventType.HOME_RUN:
                        df["at_bats"] += 1
                        df["plate_appearances"] += 1
                        df["home_runs"] += 1
                    case EventType.SACRIFICE:
                        df["plate_appearances"] += 1
                        df["sacrifice_flies"] += 1
                    case (
                        EventType.OUT
                        | EventType.GROUNDOUT
                        | EventType.LINEOUT
                        | EventType.FLYOUT
                        | EventType.POPUP
                        | EventType.FOUL_OUT
                        | EventType.FIELDERS_CHOICE
                    ):
                        df["at_bats"] += 1
                        df["plate_appearances"] += 1
                    case EventType.STRIKEOUT:
                        df["at_bats"] += 1
                        df["plate_appearances"] += 1
                        df["strikeouts"] += 1
                    case EventType.WALK:
                        df["plate_appearances"] += 1
                        df["bases_on_balls"] += 1
                    case EventType.HIT_BY_PITCH:
                        df["plate_appearances"] += 1
                        df["hit_by_pitches"] += 1
                    case _:
                        pass

                df["hits"] += play.is_hit
                df["rbi"] += play.runs_scored

    return pd.DataFrame([df])


def batting_counting_stats(games: GamesCollection) -> pd.DataFrame:
    """
    Calculates batting counting statistics for all players in a collection of games.

    Args:
        games (GamesCollection): The collection of games to calculate the statistics over.

    Returns:
        pd.DataFrame: A DataFrame containing all players' batting counting statistics.
    """

    df = {}

    for game in games:
        for name in {play.batter_name for play in game.plays}:
            if name not in df:
                df[name] = {
                    "games": 0,
                    "at_bats": 0,
                    "plate_appearances": 0,
                    "hits": 0,
                    "singles": 0,
                    "doubles": 0,
                    "triples": 0,
                    "home_runs": 0,
                    "strikeouts": 0,
                    "bases_on_balls": 0,
                    "hit_by_pitches": 0,
                    "rbi": 0,
                    "sacrifice_flies": 0,
                }

            df[name]["games"] += 1

        for play in game.plays:
            match play.event_type:
                case EventType.SINGLE:
                    df[play.batter_name]["at_bats"] += 1
                    df[play.batter_name]["plate_appearances"] += 1
                    df[play.batter_name]["singles"] += 1
                case EventType.DOUBLE:
                    df[play.batter_name]["at_bats"] += 1
                    df[play.batter_name]["plate_appearances"] += 1
                    df[play.batter_name]["doubles"] += 1
                case EventType.TRIPLE:
                    df[play.batter_name]["at_bats"] += 1
                    df[play.batter_name]["plate_appearances"] += 1
                    df[play.batter_name]["triples"] += 1
                case EventType.HOME_RUN:
                    df[play.batter_name]["at_bats"] += 1
                    df[play.batter_name]["plate_appearances"] += 1
                    df[play.batter_name]["home_runs"] += 1
                case EventType.SACRIFICE:
                    df[play.batter_name]["plate_appearances"] += 1
                    df[play.batter_name]["sacrifice_flies"] += 1
                case (
                    EventType.OUT
                    | EventType.GROUNDOUT
                    | EventType.LINEOUT
                    | EventType.FLYOUT
                    | EventType.POPUP
                    | EventType.FOUL_OUT
                    | EventType.FIELDERS_CHOICE
                ):
                    df[play.batter_name]["at_bats"] += 1
                    df[play.batter_name]["plate_appearances"] += 1
                case EventType.STRIKEOUT:
                    df[play.batter_name]["at_bats"] += 1
                    df[play.batter_name]["plate_appearances"] += 1
                    df[play.batter_name]["strikeouts"] += 1
                case EventType.WALK:
                    df[play.batter_name]["plate_appearances"] += 1
                    df[play.batter_name]["bases_on_balls"] += 1
                case EventType.HIT_BY_PITCH:
                    df[play.batter_name]["plate_appearances"] += 1
                    df[play.batter_name]["hit_by_pitches"] += 1
                case _:
                    pass

            df[play.batter_name]["hits"] += play.is_hit
            df[play.batter_name]["rbi"] += play.runs_scored

    return pd.DataFrame(df).T.sort_index()


def player_batting_rate_stats(player_name: str, games: GamesCollection) -> pd.DataFrame:
    """
    Calculates batting rate statistics for a particular player over a collection of games.

    Args:
        player_name (str): The name of the player to calculate statistics for.
        games (GamesCollection): The collection of games to calculate statistics over.

    Returns:
        pd.DataFrame: A DataFrame containing the player's batting rate statistics.
    """

    counting_stats = player_batting_counting_stats(player_name, games)

    avg = counting_stats["hits"] / counting_stats["at_bats"]
    obp = (
        counting_stats["hits"]
        + counting_stats["bases_on_balls"]
        + counting_stats["hit_by_pitches"]
    ) / (
        counting_stats["at_bats"]
        + counting_stats["bases_on_balls"]
        + counting_stats["hit_by_pitches"]
        + counting_stats["sacrifice_flies"]
    )
    slg = (
        counting_stats["singles"]
        + 2 * counting_stats["doubles"]
        + 3 * counting_stats["triples"]
        + 4 * counting_stats["home_runs"]
    ) / counting_stats["at_bats"]
    ops = obp + slg

    all_plays = get_all_plays(games)
    re24 = calculate_re24(all_plays)
    run_values, event_type_counts = calculate_run_values_and_counts(all_plays, re24)
    league_woba = calculate_league_woba(run_values, event_type_counts)
    league_obp = calculate_league_obp(event_type_counts)
    weights = calculate_woba_weights(run_values, league_woba, league_obp)
    woba = calculate_woba(
        weights,
        counting_stats["bases_on_balls"],
        counting_stats["hit_by_pitches"],
        counting_stats["singles"],
        counting_stats["doubles"],
        counting_stats["triples"],
        counting_stats["home_runs"],
        counting_stats["at_bats"],
        counting_stats["sacrifice_flies"],
    )
    print(woba)

    df = {
        "avg": avg,
        "obp": obp,
        "slg": slg,
        "ops": ops,
        "woba": woba,
    }

    df = {k: round(v, 3) for k, v in df.items()}
    return pd.DataFrame(df)


def batting_rate_stats(
    games: GamesCollection, *, filter_qualified: bool = True
) -> pd.DataFrame:
    """
    Calculates batting rate statistics for all players in a collection of games.

    Args:
        games (GamesCollection): The collection of games to calculate the statistics over.
        filter_qualified (bool, optional): If True, only calculates statistics for qualified players (those with at least 3.1 plate appearances per team game). Defaults to True.

    Returns:
        pd.DataFrame: A DataFrame containing all players' batting rate statistics.
    """

    counting_stats = batting_counting_stats(games)

    # get team games per player
    merged = players().reset_index().set_index("Player")
    merged = merged.merge(counting_stats, left_index=True, right_index=True)
    standings_ = standings()
    standings_["team_games"] = standings_["W"] + standings_["L"] + standings_["T"]
    merged = merged.merge(standings_, left_on="Team", right_index=True)
    merged = merged[["plate_appearances", "team_games"]]
    merged["qualified"] = (merged["plate_appearances"] / merged["team_games"]) >= 3.1
    merged = merged[["qualified"]]
    counting_stats = counting_stats.merge(merged, left_index=True, right_index=True)

    if filter_qualified:
        counting_stats = counting_stats[counting_stats["qualified"]]

    avg = counting_stats["hits"] / counting_stats["at_bats"]
    obp = (
        counting_stats["hits"]
        + counting_stats["bases_on_balls"]
        + counting_stats["hit_by_pitches"]
    ) / (
        counting_stats["at_bats"]
        + counting_stats["bases_on_balls"]
        + counting_stats["hit_by_pitches"]
        + counting_stats["sacrifice_flies"]
    )
    slg = (
        counting_stats["singles"]
        + 2 * counting_stats["doubles"]
        + 3 * counting_stats["triples"]
        + 4 * counting_stats["home_runs"]
    ) / counting_stats["at_bats"]
    ops = obp + slg

    all_plays = get_all_plays(games)
    re24 = calculate_re24(all_plays)
    run_values, event_type_counts = calculate_run_values_and_counts(all_plays, re24)
    league_woba = calculate_league_woba(run_values, event_type_counts)
    league_obp = calculate_league_obp(event_type_counts)
    weights = calculate_woba_weights(run_values, league_woba, league_obp)
    woba = calculate_woba(
        weights,
        counting_stats["bases_on_balls"],
        counting_stats["hit_by_pitches"],
        counting_stats["singles"],
        counting_stats["doubles"],
        counting_stats["triples"],
        counting_stats["home_runs"],
        counting_stats["at_bats"],
        counting_stats["sacrifice_flies"],
    )

    df = {
        "avg": avg,
        "obp": obp,
        "slg": slg,
        "ops": ops,
        "woba": woba,
        "qualified": counting_stats["qualified"],
    }

    df = {k: round(v, 3) for k, v in df.items()}
    return pd.DataFrame(df)
