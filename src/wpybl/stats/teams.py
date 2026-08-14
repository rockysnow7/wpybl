"""Functions for fetching team statistics."""

from bs4 import BeautifulSoup
from ..cache import _get_url

import pandas as pd


TEAM_IDS = {
    "Boston Hunters": "9f08or2mffx81409",
    "Los Angeles Queens": "v4gisr4rbgmn67b0",
    "New York Heights": "fttth861nft1j2s7",
    "San Francisco Firebells": "vhubhz8li07tmgq8",
}


def current_standings() -> pd.DataFrame:
    """Fetches the current standings."""

    url = "https://stats.womensprobaseballleague.com"
    text = _get_url(url)
    soup = BeautifulSoup(text, "html.parser")

    table = soup.find("table", {"class": "standings-table"})
    rows = table.find_all("tr")  # type: ignore
    headers = [th.text.strip() for th in rows[0].find_all("th")]
    data = rows[1:]

    df = {header: [] for header in headers}
    for row in data:
        tds = row.find_all("td")
        for header, cell in zip(headers, tds):
            df[header].append(cell.text.strip())

    df = pd.DataFrame(df).set_index("Team")
    df["W"] = df["W"].astype(int)
    df["L"] = df["L"].astype(int)
    df["T"] = df["T"].astype(int)
    df["PCT"] = df["PCT"].astype(float)
    df["GB"] = df["GB"].replace("—", 0).astype(float)
    df["RF"] = df["RF"].astype(int)
    df["RA"] = df["RA"].astype(int)
    df["DIFF"] = df["DIFF"].astype(int)
    df["H"] = df["H"].astype(int)
    df["E"] = df["E"].astype(int)
    df["LOB"] = df["LOB"].astype(int)

    return df


def players(team_name: str | None = None) -> pd.DataFrame:
    """
    Fetches basic information about the players in the league or a given team.

    Args:
        team_name (str, optional): The name of the team to fetch the players for. If not specified, fetches all players in the league. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the players' basic information.
    """

    url = "https://stats.womensprobaseballleague.com/explorer/players"
    if team_name is not None:
        team_id = TEAM_IDS[team_name]
        url += f"?team_id={team_id}"

    text = _get_url(url)
    soup = BeautifulSoup(text, "html.parser")

    table = soup.find("table", {"class": "data-table fan-table"})
    rows = table.find_all("tr")  # type: ignore
    headers = [th.text.strip() for th in rows[0].find_all("th")]
    data = rows[1:]

    df = {header: [] for header in headers}
    for row in data:
        tds = row.find_all("td")
        for header, cell in zip(headers, tds):
            df[header].append(cell.text.strip())

    df = pd.DataFrame(df)
    df = df[
        [
            "#",
            "Player",
            "Position",
            "Team",
        ]
    ]
    df["#"] = df["#"].astype(int)

    df.set_index(["Team", "#"], inplace=True)
    df = df.sort_index()

    return df
