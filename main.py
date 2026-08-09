from data import GamesCollection
from stats.batting import batting_counting_stats
from stats.pitching import (
    pitching_counting_stats,
    player_pitching_counting_stats,
    pitching_rate_stats,
    player_pitching_rate_stats,
)


if __name__ == "__main__":
    games = GamesCollection.all(frozen=True)

    name = "Gigi Schiano"
    print(player_pitching_counting_stats(name, games))
    # print(player_pitching_rate_stats(name, games))

    # print(
    #     pitching_rate_stats(games).sort_values(
    #         ["era", "whip", "k/bb"], ascending=[True, True, False]
    #     )
    # )
