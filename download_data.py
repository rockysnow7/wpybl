from dataclasses import dataclass

import bs4
import json
import os
import requests


__API_URL = "https://stats.womensprobaseballleague.com/v1/games/{game_id}/boxscore"


"""Fetches the game JSON from the API and saves it to a file. If the file already exists, it does nothing."""
def __get_game_json(game_id: str, *, timeout: int = 1) -> None:
    if os.path.exists(f"data/{game_id}.json"):
        return

    url = __API_URL.format(game_id=game_id)
    game = requests.get(url, timeout=timeout).json()
    os.makedirs("data", exist_ok=True)
    with open(f"data/{game_id}.json", "w") as f:
        json.dump(game, f)


@dataclass
class GameID:
    game_id: str
    final: bool

    def __hash__(self):
        return hash((self.game_id, self.final))

def __get_all_game_ids() -> set[GameID]:
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
        game_ids.add(GameID(game_id=game_id, final=status.lower() == "final"))

    return game_ids


def download_all_games(*, timeout: int = 1) -> None:
    for game_id in __get_all_game_ids():
        if not game_id.final:
            continue
        __get_game_json(game_id.game_id, timeout=timeout)
