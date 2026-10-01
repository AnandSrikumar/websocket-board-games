import asyncpg
from fastapi import Request
from fastapi.responses import JSONResponse

CONSTRAINT_MAP = {
    # users
    "users_username_unique": "Username already exists.",
    "users_email_unique": "Email already exists.",
    # game
    "game_name_unique": "Game name already exists.",
    # series
    "series_game_fk": "The specified game does not exist.",
    "series_player1_fk": "Player 1 does not exist.",
    "series_player2_fk": "Player 2 does not exist.",
    "series_different_players": "Players must be different.",
    "series_target_wins_positive": "Target wins must be greater than zero.",
    "series_dates_valid": "Series end time cannot be before its start time.",
    # match
    "match_series_fk": "The specified series does not exist.",
    "match_winner_fk": "The specified winner does not exist.",
    "match_dates_valid": "Match end time cannot be before its start time.",
    "match_finished_state_valid": "Invalid match completion state.",
}


async def handle_postgres_error(
    request: Request,
    exc: asyncpg.PostgresError,
) -> JSONResponse:

    constraint_name = getattr(exc, "constraint_name", None)
    db_error = "Database operation failed."
    message = CONSTRAINT_MAP.get(
        constraint_name,
        db_error,
    )
    if message == db_error:
        return JSONResponse(status_code=500, content={"error": message})

    return JSONResponse(
        status_code=400,
        content={
            "error": message,
        },
    )
