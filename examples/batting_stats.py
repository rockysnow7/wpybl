from wpybl.data import GamesCollection
from wpybl.stats.batting import (
    player_batting_counting_stats,
    player_batting_rate_stats,
    batting_counting_stats,
    batting_rate_stats,
)


if __name__ == "__main__":
    games = GamesCollection.all()

    df_counting_benites = player_batting_counting_stats("Denae Benites", games)
    print(df_counting_benites)
    #    games  at_bats  plate_appearances  hits  singles  doubles  triples  home_runs  strikeouts  bases_on_balls  hit_by_pitches  rbi  sacrifice_flies
    # 0      4       17                 18    14        9        0        0          5           1               0               0   11                1

    df_rate_benites = player_batting_rate_stats("Denae Benites", games)
    print(df_rate_benites)
    #      avg    obp    slg    ops
    # 0  0.824  0.778  1.706  2.484

    df_counting_league = batting_counting_stats(games)
    print(df_counting_league)
    #                     games  at_bats  plate_appearances  hits  singles  doubles  triples  home_runs  strikeouts  bases_on_balls  hit_by_pitches  rbi  sacrifice_flies
    # Adelaide Frank          2        5                  6     2        2        0        0          0           1               1               0    0                0
    # Alexia Jorge            3       10                 12     5        4        1        0          0           2               1               1    1                0
    # Alli Schroder           3        6                  9     0        0        0        0          0           3               2               1    0                0
    # Alyssa Zettlemoyer      4        8                 11     3        2        1        0          0           0               1               1    1                1
    # ...

    df_rate_league = batting_rate_stats(games)
    print(df_rate_league)
    #                       avg    obp    slg    ops
    # Alexia Jorge        0.500  0.583  0.600  1.183
    # Amanda Gianelloni   0.385  0.471  0.615  1.086
    # Ashton Lansdell     0.308  0.471  0.308  0.778
    # Denae Benites       0.824  0.778  1.706  2.484
    # ...
