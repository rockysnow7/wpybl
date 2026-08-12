from wpybl.data import GamesCollection
from wpybl.stats.pitching import (
    player_pitching_counting_stats,
    player_pitching_rate_stats,
    pitching_counting_stats,
    pitching_rate_stats,
)


if __name__ == "__main__":
    games = GamesCollection.all()

    df_counting_kim = player_pitching_counting_stats("Rakyung Kim", games)
    print(df_counting_kim)
    #    games  innings_pitched  hits_allowed  runs_allowed  earned_runs_allowed  bases_on_balls  strikeouts
    # 0      2              9.1             5            10                    6               5           6

    df_rate_kim = player_pitching_rate_stats("Rakyung Kim", games)
    print(df_rate_kim)
    #     era  whip  k/bb
    # 0  5.79  1.07   1.2

    df_counting_league = pitching_counting_stats(games)
    print(df_counting_league)
    #                     games  innings_pitched  hits_allowed  runs_allowed  earned_runs_allowed  bases_on_balls  strikeouts
    # Alli Schroder           2              3.1            11            11                   10               5           1
    # Alyssa Zettlemoyer      1              1.2             2             0                    0               1           0
    # Andreanne Leblanc       1              1.0             0             0                    0               1           1
    # Ayami Sato              2              8.0            14             8                    4               1           5
    # ...

    df_rate_league = pitching_rate_stats(games)
    print(df_rate_league)
    #                       era  whip  k/bb
    # Alli Schroder       27.00  4.80  0.20
    # Alyssa Zettlemoyer   0.00  1.80  0.00
    # Andreanne Leblanc    0.00  1.00  1.00
    # Ayami Sato           4.50  1.88  5.00
    # ...
