from collections import defaultdict

from src.games.exceptions import MaxPlayersReachedException
from src.games.game import GameBase
from src.games.response_classes import GameResult, MakeMoveResponse
from src.log import get_logger

log = get_logger(__name__)


class TicTacToe(GameBase):
    def __init__(self, match_id: int):
        super().__init__(match_id)
        self._players_joined = 0
        self._symbols = ["X", "O"]
        self._player_symbol_map = {}
        self._symbol_player_map = {}
        self._last_player_name = None
        self._board = [[None, None, None], [None, None, None], [None, None, None]]
        self._is_finished = False
        self._player_stats = defaultdict(int)

    def add_player(self, player_name: str):
        if self._players_joined >= 2:
            raise MaxPlayersReachedException("Maximum number of players reached...")
        symbol = self._symbols.pop()
        self._player_symbol_map[player_name] = symbol
        self._symbol_player_map[symbol] = player_name
        self._players_joined += 1
        return {"status": "success", "player_name": player_name}

    @property
    def board(self):
        return self._board

    @property
    def match_id(self):
        return self._match_id

    @property
    def players(self):  # will return {anand: X, sri: O}
        return self._player_symbol_map

    def get_players_stats(self): ...

    def get_result(self):
        def structure_complete_response(winner, is_done, win_state):
            return GameResult(
                self._match_id, winner=winner, is_finished=is_done, win_state=win_state
            )

        # horizontal
        for idx, row in enumerate(self._board):
            first = row[0]
            if first is None:
                continue
            for col in row:
                if col != first:
                    break
            else:
                return structure_complete_response(
                    self._last_player_name, True, {"direction": "H", "idx": idx}
                )
        # vertical
        for col in range(3):
            first = self._board[0][col]
            if first is None:
                continue
            for row in range(3):
                if self._board[row][col] != first:
                    break
            else:
                return structure_complete_response(
                    self._last_player_name, True, {"direction": "V", "idx": col}
                )

        # r diag
        first = self._board[0][0]
        if first is not None:
            for x in range(3):
                if self._board[x][x] != first:
                    break
            else:
                return structure_complete_response(
                    self._last_player_name, True, {"direction": "RD", "idx": None}
                )

        # ldiag
        first = self._board[0][2]
        if first is not None:
            r = 0
            c = 2
            is_diag = True
            while r < 3 and c >= 0:
                if self._board[r][c] != first:
                    is_diag = False
                    break
                r += 1
                c -= 1
            if is_diag:
                return structure_complete_response(
                    self._last_player_name, True, {"direction": "LD", "idx": None}
                )

        for row in self._board:
            for col in row:
                if col is None:
                    return structure_complete_response(
                        None, False, {"direction": "", "idx": None}
                    )
        return structure_complete_response(None, True, {"direction": "", "idx": None})

    def make_move(self, player_name: str, payload: dict) -> MakeMoveResponse:
        if self._last_player_name == player_name:
            return MakeMoveResponse(
                match_id=self._match_id,
                move=payload,
                move_maker=player_name,
                message="Not your turn",
                is_success=False,
            )
        if player_name not in self._player_symbol_map:
            return MakeMoveResponse(
                match_id=self._match_id,
                move=payload,
                move_maker=player_name,
                message=f"Player: {player_name} not joined",
                is_success=False,
            )

        row = payload["row"]
        col = payload["col"]
        symbol = self._player_symbol_map[player_name]
        if self._board[row][col] is not None:
            return MakeMoveResponse(
                match_id=self._match_id,
                move=payload,
                move_maker=player_name,
                message=f"Cell already filled with '{self._board[row][col]}'",
                is_success=False,
            )

        self._board[row][col] = symbol
        self._last_player_name = player_name
        self._player_stats[player_name] += 1
        return MakeMoveResponse(
            match_id=self._match_id,
            move=payload,
            move_maker=player_name,
            message=f"Success: Cell filled with '{self._board[row][col]}'",
            is_success=True,
        )
