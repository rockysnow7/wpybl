from data import load_all_games
from stats.batting import player_batting_counting_stats, player_batting_pct_stats


if __name__ == "__main__":
    games = load_all_games()

    # stats = player_batting_counting_stats("Isabella Villarreal", games)
    stats = player_batting_pct_stats("Amanda Gianelloni", games)
    print(stats)
