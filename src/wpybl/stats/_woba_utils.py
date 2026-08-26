from copy import deepcopy
from wpybl.data import GamesCollection

import numpy as np
import pandas as pd


def get_all_plays(games: GamesCollection) -> pd.DataFrame:
    games = sorted(games, key=lambda x: x.game_id)
    plays = [game.plays_to_df().sort_index().reset_index() for game in games]
    for game, df in zip(games, plays):
        df["game_id"] = game.game_id
    df = pd.concat(plays)

    return df


def _get_plays_for_re24(all_plays: pd.DataFrame) -> pd.DataFrame:
    all_plays = deepcopy(all_plays)
    all_plays = all_plays[
        [
            "game_id",
            "inning",
            "half",
            "outs",
            "sequence",
            "first_base",
            "second_base",
            "third_base",
            "runs_scored",
        ]
    ]

    all_plays["first_base"] = all_plays["first_base"] != ""
    all_plays["second_base"] = all_plays["second_base"] != ""
    all_plays["third_base"] = all_plays["third_base"] != ""

    df = all_plays[all_plays["outs"] != 3]
    df["state"] = (
        (df["third_base"].map(lambda x: "3" if x else "-"))
        + (df["second_base"].map(lambda x: "2" if x else "-"))
        + (df["first_base"].map(lambda x: "1" if x else "-"))
        + "/"
        + df["outs"].astype(str)
    )

    df = df[
        [
            "game_id",
            "sequence",
            "inning",
            "half",
            "state",
            "runs_scored",
        ]
    ]
    return df


def calculate_re24(all_plays: pd.DataFrame) -> pd.DataFrame:
    all_plays = _get_plays_for_re24(all_plays)
    all_plays.to_csv("new.csv", index=False)

    all_plays["runs_remaining"] = all_plays.groupby(["game_id", "inning", "half"])[
        "runs_scored"
    ].transform(lambda x: x[::-1].cumsum()[::-1])
    re24_ = all_plays.groupby("state")["runs_remaining"].mean().to_frame().reset_index()

    return re24_


# outs that don't advance runners
_OUTS = [
    "sacrifice",
    "out",
    "groundout",
    "lineout",
    "flyout",
    "popup",
    "foul_out",
    "strikeout",
]


def _get_plays_for_run_values(all_plays: pd.DataFrame) -> pd.DataFrame:
    all_plays = deepcopy(all_plays)
    all_plays = all_plays[
        [
            "game_id",
            "inning",
            "half",
            "outs",
            "sequence",
            "first_base",
            "second_base",
            "third_base",
            "event_type",
            "runs_scored",
        ]
    ]
    all_plays["first_base"] = all_plays["first_base"] != ""
    all_plays["second_base"] = all_plays["second_base"] != ""
    all_plays["third_base"] = all_plays["third_base"] != ""

    df = all_plays[all_plays["outs"] != 3]
    df["state"] = (
        (df["third_base"].map(lambda x: "3" if x else "-"))
        + (df["second_base"].map(lambda x: "2" if x else "-"))
        + (df["first_base"].map(lambda x: "1" if x else "-"))
        + "/"
        + df["outs"].astype(str)
    )

    df = df.sort_values(["game_id", "sequence"]).reset_index(drop=True)
    next_half = df.groupby("game_id")["half"].shift(-1)
    df["next_state"] = df.groupby("game_id")["state"].shift(-1)
    df["half_over"] = (df["half"] != next_half) | next_half.isna()

    df.dropna(
        subset=[
            "game_id",
            "sequence",
            "inning",
            "half",
            "state",
            "event_type",
            "runs_scored",
        ],
        inplace=True,
    )

    df = df[
        [
            "game_id",
            "sequence",
            "inning",
            "half",
            "state",
            "event_type",
            "runs_scored",
            "next_state",
            "half_over",
        ]
    ]
    return df


def calculate_run_values_and_counts(
    all_plays: pd.DataFrame,
    re24: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_plays = _get_plays_for_run_values(all_plays)

    all_plays["event_type"] = np.where(
        all_plays["event_type"].isin(_OUTS),
        "out",
        all_plays["event_type"],
    )

    re24 = {k: v for k, v in re24.to_dict("tight")["data"]}  # type: ignore
    all_plays["re_before"] = all_plays["state"].map(re24)  # type: ignore
    all_plays["re_after"] = all_plays["runs_scored"] + all_plays["next_state"].map(re24)  # type: ignore
    all_plays["re_after"] = np.where(all_plays["half_over"], 0.0, all_plays["re_after"])

    all_plays = all_plays[["event_type", "re_before", "re_after"]]
    all_plays["run_value"] = all_plays["re_after"] - all_plays["re_before"]

    run_values = (
        all_plays.groupby("event_type")
        .agg({"run_value": "mean"})
        .sort_values("run_value", ascending=True)
        .reset_index()
    )
    counts = all_plays["event_type"].value_counts().to_frame().reset_index()

    return run_values, counts


def calculate_league_woba(
    run_values: pd.DataFrame,
    event_type_counts: pd.DataFrame,
) -> float:
    # weight relative to out
    run_values = deepcopy(run_values)

    out_value = run_values[run_values["event_type"] == "out"]["run_value"].at[1]
    run_values["run_value"] = run_values["run_value"] - out_value  # type: ignore
    run_values = run_values[
        run_values["event_type"].isin(
            [
                "walk",
                "hit_by_pitch",
                "single",
                "double",
                "triple",
                "home_run",
            ]
        )
    ]
    run_values = {k: v for k, v in run_values.to_dict("tight")["data"]}  # type: ignore

    # calculate league wOBA
    event_type_counts = {k: v for k, v in event_type_counts.to_dict("tight")["data"]}  # type: ignore

    numerator = sum(
        event_type_counts[event_type] * run_values[event_type]  # type: ignore
        for event_type in run_values
    )

    denominator = (
        event_type_counts.get("out", 0)  # this already includes sacrifices
        + event_type_counts.get("single", 0)
        + event_type_counts.get("double", 0)
        + event_type_counts.get("triple", 0)
        + event_type_counts.get("home_run", 0)
        + event_type_counts.get("fielders_choice", 0)
        + event_type_counts.get("walk", 0)
        + event_type_counts.get("hit_by_pitch", 0)
    )

    woba = numerator / denominator
    return woba  # type: ignore


def calculate_league_obp(event_type_counts: pd.DataFrame) -> float:
    counts = {k: v for k, v in event_type_counts.to_dict("tight")["data"]}  # type: ignore

    numerator = (
        counts.get("single", 0)
        + counts.get("double", 0)
        + counts.get("triple", 0)
        + counts.get("home_run", 0)
        + counts.get("walk", 0)
        + counts.get("hit_by_pitch", 0)
    )
    denominator = (
        counts.get("out", 0)  # this already includes sacrifices
        + counts.get("single", 0)
        + counts.get("double", 0)
        + counts.get("triple", 0)
        + counts.get("home_run", 0)
        + counts.get("fielders_choice", 0)
        + counts.get("walk", 0)
        + counts.get("hit_by_pitch", 0)
    )

    return numerator / denominator


def calculate_woba_weights(
    run_values: pd.DataFrame,
    league_woba: float,
    league_obp: float,
) -> dict[str, float]:
    scale = league_obp / league_woba

    # weight relative to out
    run_values = deepcopy(run_values)

    out_value = run_values[run_values["event_type"] == "out"]["run_value"].at[1]
    run_values["run_value"] = run_values["run_value"] - out_value  # type: ignore
    run_values = run_values[
        run_values["event_type"].isin(
            [
                "walk",
                "hit_by_pitch",
                "single",
                "double",
                "triple",
                "home_run",
            ]
        )
    ]
    run_values = {k: v for k, v in run_values.to_dict("tight")["data"]}  # type: ignore

    weights = pd.DataFrame(
        {
            "event_type": run_values.keys(),
            "weight": [value * scale for value in run_values.values()],  # type: ignore
        }
    )
    weights = {k: v for k, v in weights.to_dict("tight")["data"]}
    return weights


def calculate_woba(
    weights: dict[str, float],
    walks: pd.Series,
    hit_by_pitches: pd.Series,
    singles: pd.Series,
    doubles: pd.Series,
    triples: pd.Series,
    home_runs: pd.Series,
    at_bats: pd.Series,
    sacrifice_flies: pd.Series,
) -> pd.Series:
    numerator = (
        weights.get("walk", 0) * walks
        + weights.get("hit_by_pitch", 0) * hit_by_pitches
        + weights.get("single", 0) * singles
        + weights.get("double", 0) * doubles
        + weights.get("triple", 0) * triples
        + weights.get("home_run", 0) * home_runs
    )
    denominator = at_bats + walks + hit_by_pitches + sacrifice_flies
    woba = numerator / denominator

    return woba
