class MaxPlayersReachedException(Exception):
    """Raised when a game cannot accept any more players."""

    pass


class NotYourTurn(Exception):
    pass
