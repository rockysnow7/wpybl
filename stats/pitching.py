"""Functions to calculate pitching statistics from game data."""

import pandas as pd

from data import GamesCollection


def __innings_pitched_as_decimal(innings_pitched: float) -> float:
    """Converts a fractional innings pitched value to a decimal value (e.g., 3.2 to 3.66666...)."""

    innings_pitched_int = int(innings_pitched)
    innings_pitched_frac = 10 * (innings_pitched - innings_pitched_int)
    ip = innings_pitched_int + innings_pitched_frac / 3

    return ip


def player_pitching_counting_stats(
    player_name: str, games: GamesCollection
) -> pd.DataFrame:
    """
    Calculates pitching counting statistics for a particular player over a collection of games.

    Args:
        player_name (str): The name of the player to calculate statistics for.
        games (GamesCollection): The collection of games to calculate statistics over.

    Returns:
        pd.DataFrame: A DataFrame containing the player's pitching counting statistics.
    """

    df = {
        "games": 0,
        "innings_pitched": 0.0,
        "hits_allowed": 0,
        "runs_allowed": 0,
        "earned_runs_allowed": 0,
        "bases_on_balls": 0,
        "strikeouts": 0,
    }

    for game in games:
        player = game.get_player(player_name)
        if player is None:
            continue
        if player.pitching is None:
            continue

        df["games"] += 1
        df["innings_pitched"] += player.pitching.innings_pitched
        df["hits_allowed"] += player.pitching.hits_allowed
        df["runs_allowed"] += player.pitching.runs_allowed
        df["earned_runs_allowed"] += player.pitching.earned_runs_allowed
        df["bases_on_balls"] += player.pitching.bases_on_balls
        df["strikeouts"] += player.pitching.strikeouts

    df["innings_pitched"] = round(df["innings_pitched"], 1)

    return pd.DataFrame([df])


def pitching_counting_stats(games: GamesCollection) -> pd.DataFrame:
    """
    Calculates pitching counting statistics for all players in a collection of games.

    Args:
        games (GamesCollection): The collection of games to calculate the statistics over.

    Returns:
        pd.DataFrame: A DataFrame containing all players' pitching counting statistics.
    """

    df = {}

    for game in games:
        for team in game.teams:
            for player in team.players:
                if player.pitching is None:
                    continue
                if player.name not in df:
                    df[player.name] = {
                        "games": 0,
                        "innings_pitched": 0.0,
                        "hits_allowed": 0,
                        "runs_allowed": 0,
                        "earned_runs_allowed": 0,
                        "bases_on_balls": 0,
                        "strikeouts": 0,
                    }

                df[player.name]["games"] += 1
                df[player.name]["innings_pitched"] += player.pitching.innings_pitched
                df[player.name]["hits_allowed"] += player.pitching.hits_allowed
                df[player.name]["runs_allowed"] += player.pitching.runs_allowed
                df[player.name]["earned_runs_allowed"] += (
                    player.pitching.earned_runs_allowed
                )
                df[player.name]["bases_on_balls"] += player.pitching.bases_on_balls
                df[player.name]["strikeouts"] += player.pitching.strikeouts

    df = pd.DataFrame(df).T.sort_index()

    df["innings_pitched"] = df["innings_pitched"].map(lambda x: round(x, 1))
    cols = df.columns.difference(["innings_pitched"])
    df[cols] = df[cols].astype(int)

    return df


def player_pitching_rate_stats(
    player_name: str, games: GamesCollection
) -> pd.DataFrame:
    """
    Calculates pitching rate statistics for a particular player over a collection of games.

    Args:
        player_name (str): The name of the player to calculate statistics for.
        games (GamesCollection): The collection of games to calculate statistics over.

    Returns:
        pd.DataFrame: A DataFrame containing the player's pitching rate statistics.
    """

    counting_stats = player_pitching_counting_stats(player_name, games)
    counting_stats["innings_pitched"] = counting_stats["innings_pitched"].map(
        __innings_pitched_as_decimal
    )

    era = 9 * counting_stats["earned_runs_allowed"] / counting_stats["innings_pitched"]
    whip = (
        counting_stats["bases_on_balls"] + counting_stats["hits_allowed"]
    ) / counting_stats["innings_pitched"]
    k_per_bb = counting_stats["strikeouts"] / counting_stats["bases_on_balls"]

    df = {
        "era": era,
        "whip": whip,
        "k/bb": k_per_bb,
    }

    df = {k: round(v, 2) for k, v in df.items()}
    return pd.DataFrame(df)


def pitching_rate_stats(
    games: GamesCollection, *, filter_qualified: bool = True
) -> pd.DataFrame:
    """
    Calculates pitching rate statistics for all players in a collection of games.

    Args:
        games (GamesCollection): The collection of games to calculate the statistics over.
        filter_qualified (bool, optional): If True, only calculates statistics for qualified players (those with at least 1 inning pitched per game). Defaults to True.

    Returns:
        pd.DataFrame: A DataFrame containing all players' pitching rate statistics.
    """

    counting_stats = pitching_counting_stats(games)
    if filter_qualified:
        counting_stats = counting_stats[
            (counting_stats["innings_pitched"] / counting_stats["games"]) >= 1
        ]

    counting_stats["innings_pitched"] = counting_stats["innings_pitched"].map(
        __innings_pitched_as_decimal
    )

    era = 9 * counting_stats["earned_runs_allowed"] / counting_stats["innings_pitched"]
    whip = (
        counting_stats["bases_on_balls"] + counting_stats["hits_allowed"]
    ) / counting_stats["innings_pitched"]
    k_per_bb = counting_stats["strikeouts"] / counting_stats["bases_on_balls"]

    df = {
        "era": era,
        "whip": whip,
        "k/bb": k_per_bb,
    }

    df = {k: round(v, 2) for k, v in df.items()}
    return pd.DataFrame(df)
