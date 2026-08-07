from dataclasses import dataclass
from download_data import download_all_games
from model import Play

import json
import os


if __name__ == '__main__':
    download_all_games()

    # with open("data.json") as f:
    #     data = json.load(f)
    # plays_raw = data["boxscore"]["plays"]
    
    # plays: list[Play] = [Play.model_validate(play) for play in plays_raw]
    # print(plays[0])
