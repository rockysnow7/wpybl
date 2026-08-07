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
from data import load_all_games
from stats.batting import player_batting_pct_stats

if __name__ == "__main__":
    games = load_all_games()

    stats = player_batting_pct_stats("Amanda Gianelloni", games)
    print(stats)
    #      avg    obp    slg    ops
    # 0  0.429  0.556  0.429  0.984
```
