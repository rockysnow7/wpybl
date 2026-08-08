from data import GamesCollection
from stats.batting import batting_rate_stats


if __name__ == "__main__":
    games = GamesCollection.all(frozen=True)

    name = "Alyssa Zettlemoyer"
    # stats = player_batting_counting_stats(name, games)
    # stats = player_batting_rate_stats(name, games)
    stats = batting_rate_stats(games)
    print(stats)
