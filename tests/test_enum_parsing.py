from wpybl.cache import clear_cache
from wpybl.data import GamesCollection
from wpybl.raw.game import GameStatus
from wpybl.raw.play import EventType, PitchEventCode, PitchEventType
from wpybl.raw.team import Hand, PlayerPosition


clear_cache()  # to always get the newest games
games = GamesCollection.all()


def test_game_status_parsing() -> None:
    """Asserts that there are no unimplemented variants of `wpybl.raw.game.GameStatus`."""

    for game in games:
        assert game.status != GameStatus.WPYBL_UNKNOWN, f"error in game {game.game_id}"


def test_event_type_parsing() -> None:
    """Asserts that there are no unimplemented variants of `wpybl.raw.play.EventType`."""

    for game in games:
        for play in game.plays:
            assert play.event_type != EventType.WPYBL_UNKNOWN, (
                f"error in game {game.game_id}, play {play.sequence - 1}"
            )


def test_pitch_event_code_parsing() -> None:
    """Asserts that there are no unimplemented variants of `wpybl.raw.play.PitchEventCode`."""

    for game in games:
        for play in game.plays:
            if play.pitch_events is None:
                continue
            for pitch_event in play.pitch_events:
                assert pitch_event.code != PitchEventCode.WPYBL_UNKNOWN, (
                    f"error in game {game.game_id}, play {play.sequence - 1}"
                )


def test_pitch_event_type_parsing() -> None:
    """Asserts that there are no unimplemented variants of `wpybl.raw.play.PitchEventType`."""

    for game in games:
        for play in game.plays:
            if play.pitch_events is None:
                continue
            for pitch_event in play.pitch_events:
                assert pitch_event.type != PitchEventType.WPYBL_UNKNOWN, (
                    f"error in game {game.game_id}, play {play.sequence - 1}"
                )


def test_player_position_parsing() -> None:
    """Asserts that there are no unimplemented variants of `wpybl.raw.team.PlayerPosition`."""

    for game in games:
        for team in game.teams:
            for player in team.players:
                if player.positions is None:
                    continue
                for position in player.positions:
                    assert position != PlayerPosition.WPYBL_UNKNOWN, (
                        f"error in game {game.game_id}, team {team.name}, player {player.name}"
                    )

            for starter in team.starters:
                assert starter.position != PlayerPosition.WPYBL_UNKNOWN, (
                    f"error in game {game.game_id}, team {team.name}, starter {starter.name}"
                )


def test_hand_parsing() -> None:
    """Asserts that there are no unimplemented variants of `wpybl.raw.team.Hand`."""

    for game in games:
        for team in game.teams:
            for player in team.players:
                assert player.bats != Hand.WPYBL_UNKNOWN, (
                    f"error in game {game.game_id}, team {team.name}, player {player.name}"
                )
                assert player.throws != Hand.WPYBL_UNKNOWN, (
                    f"error in game {game.game_id}, team {team.name}, player {player.name}"
                )
