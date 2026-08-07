import pandas as pd

from raw.game import Game
from raw.play import EventType


def player_batting_counting_stats(player_name: str, games: list[Game]) -> pd.DataFrame:
    df = {
        "games": 0,
        "at_bats": 0,
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

        for play in game.plays:
            if play.batter_name == player_name:
                match play.event_type:
                    case EventType.SINGLE:
                        df["at_bats"] += 1
                        df["hits"] += 1
                        df["singles"] += 1
                    case EventType.DOUBLE:
                        df["at_bats"] += 1
                        df["hits"] += 1
                        df["doubles"] += 1
                    case EventType.TRIPLE:
                        df["at_bats"] += 1
                        df["hits"] += 1
                        df["triples"] += 1
                    case EventType.HOME_RUN:
                        df["at_bats"] += 1
                        df["hits"] += 1
                        df["home_runs"] += 1
                    case EventType.SACRIFICE:
                        df["sacrifice_flies"] += 1
                    case (
                        EventType.OUT
                        | EventType.GROUNDOUT
                        | EventType.LINEOUT
                        | EventType.FLYOUT
                        | EventType.POPUP
                        | EventType.FOUL_OUT
                        | EventType.FIELDERS_CHOICE
                        | EventType.STRIKEOUT
                    ):
                        df["at_bats"] += 1
                    case EventType.STRIKEOUT:
                        df["at_bats"] += 1
                        df["strikeouts"] += 1
                    case EventType.WALK:
                        df["bases_on_balls"] += 1
                    case EventType.HIT_BY_PITCH:
                        df["hit_by_pitches"] += 1
                    case _:
                        pass

                df["rbi"] += play.runs_scored
    return pd.DataFrame([df])


def player_batting_pct_stats(player_name: str, games: list[Game]) -> pd.DataFrame:
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

    df = {
        "avg": avg,
        "obp": obp,
        "slg": slg,
        "ops": ops,
    }

    df = {k: round(v, 3) for k, v in df.items()}
    return pd.DataFrame(df)
