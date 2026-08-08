from data import GamesCollection
from stats.batting import player_batting_counting_stats, player_batting_pct_stats


if __name__ == "__main__":
    games = GamesCollection.all()

    # stats = player_batting_counting_stats("Isabella Villarreal", games)
    stats = player_batting_pct_stats("Amanda Gianelloni", games)
    print(stats)
