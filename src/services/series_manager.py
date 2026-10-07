class SeriesManager:
    def __init__(self, series_id, player1, player2, target_wins, game):
        self._player1 = player1
        self._player2 = player2
        self._series_id = series_id
        self._target_wins = target_wins
        self._game = game
