# wpybl

A (work-in-progress) Python library for working with Women's Professional Baseball League (WPBL) data.
It aims to be equivalent to the [pybaseball](https://github.com/jldbc/pybaseball) library.
(This is fan-made and not affiliated with the WPBL.)

## Modules

- `data`: Downloads and loads game data from the WPBL API.
- `raw`: Data models to wrap the WPBL API's JSON responses.
- `stats`: Functions to calculate statistics from game data.

## Example

```python
from wpybl.data import GamesCollection
from wpybl.stats.batting import player_batting_rate_stats
from wpybl.stats.pitching import pitching_rate_stats

if __name__ == "__main__":
    games = GamesCollection.all()

    print(player_batting_rate_stats("Amanda Gianelloni", games))
    #      avg    obp    slg    ops
    # 0  0.455  0.538  0.727  1.266

    print(pitching_rate_stats(games))
    #                       era  whip  k/bb
    # Alli Schroder       27.00  4.80  0.20
    # Alyssa Zettlemoyer   0.00  1.80  0.00
    # Andreanne Leblanc    0.00  1.00  1.00
    # Ayami Sato           4.50  1.88  5.00
    # ...

    for game in games:
        game.plays_to_csv(f"{game.game_id}.csv")  # saves play-by-plays to a CSV file
```
