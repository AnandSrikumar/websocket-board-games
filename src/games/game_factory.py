from src.games.game import GameBase
from src.games.tictactoe.game import TicTacToe

GAME_MAP = {"tictactoe": TicTacToe}


def get_game(game_name: str, match_id: int) -> GameBase:
    if game_name not in GAME_MAP:
        raise AttributeError(f"Game: {game_name} not available")
    return GAME_MAP[game_name](match_id)
