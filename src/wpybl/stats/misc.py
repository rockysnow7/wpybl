"""A collection of miscellaneous stats functions."""

from ..data import GamesCollection
from ._woba_utils import (
    get_all_plays as _get_all_plays,
    calculate_re24 as _calculate_re24,
    calculate_run_values_and_counts as _calculate_run_values_and_counts,
    calculate_league_woba as _calculate_league_woba,
    calculate_league_obp as _calculate_league_obp,
    calculate_woba_weights as _calculate_woba_weights,
)

import pandas as pd


def re24(games: GamesCollection) -> pd.DataFrame:
    """
    Calculates the RE24 run expectancy matrix over the given collection of games.

    Args:
        games (GamesCollection): The collection of games to calculate the RE24 matrix over.

    Returns:
        pd.DataFrame: A DataFrame containing the RE24 matrix.
    """

    all_plays = _get_all_plays(games)
    re24 = _calculate_re24(all_plays)

    return re24.set_index("state")


def run_values(games: GamesCollection) -> pd.DataFrame:
    """
    Calculates the run values of various events over the given collection of games.

    Args:
        games (GamesCollection): The collection of games to calculate the run values over.

    Returns:
        pd.DataFrame: A DataFrame containing the run values.
    """

    all_plays = _get_all_plays(games)
    re24_ = _calculate_re24(all_plays)
    run_values, _ = _calculate_run_values_and_counts(all_plays, re24_)

    return run_values.set_index("event_type")


def woba_weights(games: GamesCollection) -> pd.DataFrame:
    """
    Calculates the linear weights of the events in the wOBA equation over the given collection of games.

    Args:
        games (GamesCollection): The collection of games to calculate the wOBA weights over.

    Returns:
        pd.DataFrame: A DataFrame containing the wOBA weights.
    """

    all_plays = _get_all_plays(games)
    re24_ = _calculate_re24(all_plays)
    run_values, event_type_counts = _calculate_run_values_and_counts(all_plays, re24_)
    league_woba = _calculate_league_woba(run_values, event_type_counts)
    league_obp = _calculate_league_obp(event_type_counts)
    weights = _calculate_woba_weights(run_values, league_woba, league_obp)

    df = pd.DataFrame([weights]).T.reset_index()
    df = df.rename(columns={"index": "event_type", 0: "weight"}).set_index("event_type")

    return df
