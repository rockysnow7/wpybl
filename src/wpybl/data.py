"""Functions to download and load game data from the WPBL API."""

from __future__ import annotations
from .cache import _get_url, _get_urls, _WPYBL_DATA_DIR
from collections.abc import Callable, Iterator
from copy import deepcopy
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


def __get_all_game_ids() -> set[str]:
    schedule_url = (
        "https://www.womensprobaseballleague.com/wp-json/wpbl/v1/calendar-events"
    )
    schedule_json = json.loads(_get_url(schedule_url))  # type: ignore
    completed_games_urls = {
        game["url"]
        for game in schedule_json
        if game["extendedProps"]["status"] == "final"
    }

    texts = _get_urls(
        list(completed_games_urls),
        cache_forever=True,
        tqdm_desc="Fetching schedule",
    )
    game_ids = set()
    for text in texts:
        soup = bs4.BeautifulSoup(text, "html.parser")
        game_id = soup.find("section", attrs={"data-game-id": True})["data-game-id"]  # type: ignore
        game_ids.add(game_id)
    return game_ids


def _download_all_games(*, timeout: int = 1) -> None:
    game_ids = __get_all_game_ids()
    final_game_ids = [game_id for game_id in game_ids]

    for game_id in tqdm(final_game_ids, desc="Downloading games"):
        __get_game_json(game_id, timeout=timeout)


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
