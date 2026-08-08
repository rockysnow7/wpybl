from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from glob import glob
from raw.game import Game

import bs4
import json
import os
import requests


__API_URL = "https://stats.womensprobaseballleague.com/v1/games/{game_id}/boxscore"


def __get_game_json(game_id: str, *, timeout: int = 1) -> None:
    """Fetches the game JSON from the API and saves it to a file. If the file already exists, it does nothing."""

    if os.path.exists(f"wpybl_data/{game_id}.json"):
        return

    url = __API_URL.format(game_id=game_id)
    game = requests.get(url, timeout=timeout).json()
    os.makedirs("wpybl_data", exist_ok=True)
    with open(f"wpybl_data/{game_id}.json", "w") as f:
        json.dump(game, f, indent=4)


@dataclass
class __GameID:
    game_id: str
    final: bool

    def __hash__(self):
        return hash((self.game_id, self.final))


def __get_all_game_ids() -> set[__GameID]:
    url = "https://stats.womensprobaseballleague.com/explorer/games"
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    game_ids = set()

    tbody = soup.find("table", attrs={"class": "data-table fan-table"}).find("tbody")
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        a = tds[2].find("a")
        game_id = a["href"].split("/")[-1]
        status = tds[3].text
        game_ids.add(__GameID(game_id=game_id, final=status.lower() == "final"))

    return game_ids


def _download_all_games(*, timeout: int = 1) -> None:
    for game_id in __get_all_game_ids():
        if not game_id.final:
            continue
        __get_game_json(game_id.game_id, timeout=timeout)


class GamesCollection:
    """A collection of games, upon which statistics can be calculated."""

    def __init__(self, games: list[Game]) -> None:
        self.games = games

    @staticmethod
    def date_range(start: date, end: date, *, frozen: bool = False) -> GamesCollection:
        """
        Returns a GamesCollection containing all games from between the start and end dates (inclusive).

        NOTE: The WPBL API only lists the last date on which a game was updated, not the date on which it was
        actually played. As games can be updated at any time, this method may not be completely accurate.

        Args:
            start (date): The start date (inclusive).
            end (date): The end date (inclusive).
            frozen (bool, optional): If True, new games will not be downloaded. Defaults to False.
        """

        if not frozen:
            _download_all_games()

        games = []
        for path in glob("wpybl_data/*.json"):
            with open(path) as f:
                data = json.load(f)
            game = Game.from_json(data)
            if start <= game.source_updated_at <= end:
                games.append(game)
        return GamesCollection(games)

    @staticmethod
    def all(*, frozen: bool = False) -> GamesCollection:
        """
        Returns a GamesCollection containing all games.

        Args:
            frozen (bool, optional): If True, new games will not be downloaded. Defaults to False.
        """

        if not frozen:
            _download_all_games()

        games = []
        for path in glob("wpybl_data/*.json"):
            with open(path) as f:
                data = json.load(f)
            game = Game.from_json(data)
            games.append(game)
        return GamesCollection(games)

    def __iter__(self) -> Iterator[Game]:
        return iter(self.games)
