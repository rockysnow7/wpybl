"""Functions to download and load game data from the WPBL API."""

from __future__ import annotations
from .cache import _get_url, _WPYBL_DATA_DIR
from collections.abc import Callable, Iterator
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from glob import glob
from pydantic import ValidationError
from .raw.game import Game
from tqdm import tqdm

import bs4
import json
import os
import requests


_GAMES_DIR = f"{_WPYBL_DATA_DIR}/games"
if not os.path.exists(_GAMES_DIR):
    os.makedirs(_GAMES_DIR)

__API_URL = "https://stats.womensprobaseballleague.com/v1/games/{game_id}/boxscore"


def __get_game_json(game_id: str, *, timeout: int = 1) -> None:
    """Fetches the game JSON from the API and saves it to a file. If the file already exists, it does nothing."""

    if os.path.exists(f"{_GAMES_DIR}/{game_id}.json"):
        return

    url = __API_URL.format(game_id=game_id)
    game = requests.get(url, timeout=timeout).json()
    os.makedirs(_GAMES_DIR, exist_ok=True)
    with open(f"{_GAMES_DIR}/{game_id}.json", "w") as f:
        json.dump(game, f, indent=4)


@dataclass
class __GameID:
    game_id: str
    final: bool

    def __hash__(self):
        return hash((self.game_id, self.final))


def __get_all_game_ids() -> set[__GameID]:
    url = "https://stats.womensprobaseballleague.com/explorer/games"
    text = _get_url(url)
    soup = bs4.BeautifulSoup(text, "html.parser")
    game_ids = set()

    tbody = soup.find("table", attrs={"class": "data-table fan-table"}).find("tbody")  # type: ignore
    for tr in tbody.find_all("tr"):  # type: ignore
        tds = tr.find_all("td")
        a = tds[2].find("a")
        game_id = a["href"].split("/")[-1]  # type: ignore
        status = tds[3].text
        final = status.lower().startswith(
            "final"
        )  # regular games say "final", extra-innings games say "final - <number> innings"
        game_ids.add(__GameID(game_id=game_id, final=final))

    return game_ids


def _download_all_games(*, timeout: int = 1) -> None:
    game_ids = __get_all_game_ids()
    final_game_ids = [game_id for game_id in game_ids if game_id.final]

    for game_id in tqdm(final_game_ids, desc="Downloading games"):
        __get_game_json(game_id.game_id, timeout=timeout)


class GamesCollection:
    """An unordered collection of games, upon which statistics can be calculated."""

    def __init__(self, games: list[Game]) -> None:
        self.games = games

    @staticmethod
    def date_range(start: date, end: date) -> GamesCollection:
        """
        Returns a GamesCollection containing all games from between the start and end dates (inclusive).

        NOTE: The WPBL API only lists the last date on which a game was updated, not the date on which it was
        actually played. As games can be updated at any time, this method may not be completely accurate.

        Args:
            start (date): The start date (inclusive).
            end (date): The end date (inclusive).
        """

        _download_all_games()

        games = []
        for path in tqdm(glob(f"{_GAMES_DIR}/*.json"), desc="Loading games"):
            with open(path) as f:
                data = json.load(f)
            game = Game.from_json(data)
            if start <= game.source_updated_at <= end:
                games.append(game)

        if not games:
            raise ValueError("No games found.")  # this should not be possible

        return GamesCollection(games)

    @staticmethod
    def all() -> GamesCollection:
        """Returns a GamesCollection containing all games."""

        _download_all_games()

        games = []
        for path in tqdm(glob(f"{_GAMES_DIR}/*.json"), desc="Loading games"):
            with open(path) as f:
                data = json.load(f)
            try:
                game = Game.from_json(data)
                games.append(game)
            except (ValidationError, ValueError):
                print(f"Failed to load {path}")

        if not games:
            raise ValueError("No games found.")  # this should not be possible

        return GamesCollection(games)

    def __iter__(self) -> Iterator[Game]:
        return iter(self.games)

    def __len__(self) -> int:
        return len(self.games)

    def filter(
        self,
        *,
        has_id: str | None = None,
        has_team: str | None = None,
        has_player: str | None = None,
        custom: Callable[[Game], bool] | list[Callable[[Game], bool]] | None = None,
    ) -> GamesCollection:
        """
        Returns a new GamesCollection containing only games that match the specified filters.
        If no filters are specified, the original GamesCollection is returned.

        Args:
            has_id (str, optional): If specified, only the game with the given ID will be included in the new GamesCollection. Defaults to None.
            has_team (str, optional): If specified, only games involving the given team will be included in the new GamesCollection. Defaults to None.
            has_player (str, optional): If specified, only games involving the given player will be included in the new GamesCollection. Defaults to None.
            custom (Callable[[Game], bool] | list[Callable[[Game], bool]], optional): If specified, only games that match the given custom filter(s) will be included in the new GamesCollection. Defaults to None.

        Returns:
            GamesCollection: A new GamesCollection containing only games that match the specified filters.
        """

        games = deepcopy(self.games)

        if has_id is not None:
            games = [game for game in self.games if game.game_id == has_id]
        if has_team is not None:
            games = [
                game
                for game in self.games
                if any(team.name == has_team for team in game.teams)
            ]
        if has_player is not None:
            games = [
                game
                for game in self.games
                if any(team.has_player(has_player) for team in game.teams)
            ]
        if custom is not None:
            if not isinstance(custom, list):
                custom = [custom]
            games = [game for game in self.games if any(f(game) for f in custom)]

        return GamesCollection(games)
