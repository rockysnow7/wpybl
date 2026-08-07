from download_data import download_all_games
from game import Game
from glob import glob
from tqdm import tqdm

import json


if __name__ == "__main__":
    download_all_games()

    for path in tqdm(glob("data/*.json")):
        print(path)
        with open(path) as f:
            data = json.load(f)
        game = Game.from_json(data)
