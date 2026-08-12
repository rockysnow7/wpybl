from wpybl.data import GamesCollection


if __name__ == "__main__":
    games = GamesCollection.all().filter(
        has_player="Gigi Schiano",
    )  # get all games featuring Gigi Schiano

    # save each game to a CSV file
    for game in games:
        path = f"{game.game_id}.csv"
        _df = game.detailed_plays_to_df(save_to_path=path)
        # sequence,pitch_sequence,inning,half,outs,batting_team_id,batter_id,batter_name,pitcher_id,pitcher_name,first_base,second_base,third_base,bases_loaded,event_type,is_hit,is_scoring_play,runs_scored,balls_pre,strikes_pre,fouls_pre,balls_post,strikes_post,fouls_post,narrative,pitch_type,pitch_release_speed,pitch_speed_unit,pitch_spin_rate_rpm,pitch_extension,pitch_distance_unit,pitch_vertical_break,pitch_horizontal_break,pitch_plate_location_height,pitch_plate_location_side,pitch_event_type,pitch_occurred_at,pitch_created_at,pitch_updated_at,hit_type,hit_exit_speed,hit_distance,hit_launch_angle_deg,hit_horizontal_angle_deg,hit_occurred_at,hit_created_at,hit_updated_at
        # 43,1,4,top,0,vhubhz8li07tmgq8,nkyvasxbczf0o2br,Joely Leguizamon,lx8fhakk17z85naw,Maïka Dumais,,,,False,,,,,0,0,0,1,0,0,,Fastball,71.0132,mph,1921.84,5.35892,feet,-50.4707,-3.78555,3.64578,0.20784,ball,2026-08-03 01:01:41.133414+00:00,2026-08-03 14:32:58.520868+00:00,2026-08-03 14:32:58.520868+00:00,,,,,,,,
        # ...
