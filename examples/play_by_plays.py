from wpybl.data import GamesCollection


if __name__ == "__main__":
    games = GamesCollection.all().filter(
        has_team="New York Heights",
    )  # get all New York Heights games

    # save each game to a CSV file
    for game in games:
        path = f"{game.game_id}.csv"
        _df = game.plays_to_df(save_to_path=path)
        # sequence,inning,half,outs,batting_team_id,batter_id,batter_name,pitcher_id,pitcher_name,first_base,second_base,third_base,pitch_sequence,final_balls,final_strikes,final_fouls,event_type,is_hit,is_scoring_play,runs_scored,narrative
        # 1,1,top,0,fttth861nft1j2s7,qo6ahavmzhlynlcv,Natsuki Yonetani,kodbwa3vuzo1kbzt,Gigi Schiano,,,,BBKSBP,3,2,0,single,True,False,0,Natsuki Yonetani singled down the lf line (3-2 BBKSB).
        # ...
