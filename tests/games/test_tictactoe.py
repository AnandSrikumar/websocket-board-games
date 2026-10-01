from src.games.tictactoe.game import TicTacToe
from src.games.exceptions import MaxPlayersReachedException
from src.games.response_classes import MakeMoveResponse

import pytest

def test_add_players():
    t = TicTacToe(1)
    p1 = t.add_player("anand")
    p2 = t.add_player("sowmya")
    
    assert t.players['anand'] == 'O'
    assert t.players['sowmya'] == 'X'

    assert p1['status'] == 'success'
    assert p2['status'] == 'success'

    with pytest.raises(MaxPlayersReachedException):
        t.add_player("player3")


def test_board():
    t = TicTacToe(1)
    assert t.board == [[None, None, None], [None, None, None], [None, None, None]]

def test_make_move():
    t = TicTacToe(1)
    t.add_player('player1')
    t.add_player('player2')
    res = t.make_move('player1', {"row": 2, "col": 2})
    assert res.match_id == 1
    
    assert res.is_success
    assert res.move_maker == 'player1'

    assert t.players['player1'] == 'O'
    assert t.board[2][2] == 'O'

    res = t.make_move("player2", {"row": 1, "col": 1})
    assert t.board[1][1] == 'X'
    assert res.is_success
    assert res.move_maker == 'player2'


def test_make_move_negative():
    t = TicTacToe(1)
    t.add_player('player1')
    t.add_player('player2')
    res = t.make_move('player1', {"row": 2, "col": 2})

    res = t.make_move("player1", {"row": 1, "col": 1})
    assert not res.is_success
    assert res.move_maker == 'player1'
    assert res.message == "Not your turn"

    res = t.make_move("player2", {"row": 2, "col": 2})
    assert not res.is_success
    assert res.message == "Cell already filled with 'O'"

    res = t.make_move("player3", {"row": 1, "col": 1})
    assert not res.is_success


def play_moves(game, moves):
    """
    moves:
        [(player, row, col), ...]
    """
    for player, row, col in moves:
        game.make_move(player, {"row": row, "col": col})


def create_game():
    game = TicTacToe(1)
    game.add_player("player1")  # O
    game.add_player("player2")  # X
    return game


def test_horizontal_win():
    game = create_game()

    moves = [
        ("player1", 0, 0),
        ("player2", 1, 0),
        ("player1", 0, 1),
        ("player2", 1, 1),
        ("player1", 0, 2),
    ]

    play_moves(game, moves)

    result = game.get_result()

    assert result.winner == "player1"
    assert result.is_finished is True
    assert result.win_state == {
        "direction": "H",
        "idx": 0,
    }


def test_vertical_win():
    game = create_game()

    moves = [
        ("player1", 0, 0),
        ("player2", 0, 1),
        ("player1", 1, 0),
        ("player2", 1, 1),
        ("player1", 2, 0),
    ]

    play_moves(game, moves)

    result = game.get_result()

    assert result.winner == "player1"
    assert result.is_finished is True
    assert result.win_state == {
        "direction": "V",
        "idx": 0,
    }


def test_right_diagonal_win():
    game = create_game()

    moves = [
        ("player1", 0, 0),
        ("player2", 0, 1),
        ("player1", 1, 1),
        ("player2", 1, 0),
        ("player1", 2, 2),
    ]

    play_moves(game, moves)

    result = game.get_result()

    assert result.winner == "player1"
    assert result.is_finished is True
    assert result.win_state == {
        "direction": "RD",
        "idx": None,
    }


def test_left_diagonal_win():
    game = create_game()

    moves = [
        ("player1", 0, 2),
        ("player2", 0, 0),
        ("player1", 1, 1),
        ("player2", 1, 0),
        ("player1", 2, 0),
    ]

    play_moves(game, moves)

    result = game.get_result()

    assert result.winner == "player1"
    assert result.is_finished is True
    assert result.win_state == {
        "direction": "LD",
        "idx": None,
    }


def test_draw():
    game = create_game()

    moves = [
        ("player1", 0, 0),
        ("player2", 0, 1),
        ("player1", 0, 2),
        ("player2", 1, 1),
        ("player1", 1, 0),
        ("player2", 1, 2),
        ("player1", 2, 1),
        ("player2", 2, 0),
        ("player1", 2, 2),
    ]

    play_moves(game, moves)

    result = game.get_result()

    assert result.winner is None
    assert result.is_finished is True

