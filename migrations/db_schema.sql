BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    username VARCHAR(50) NOT NULL,
    password_hash TEXT NOT NULL,
    email VARCHAR(255) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
    blocked_till TIMESTAMPTZ,
    is_busy BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT users_username_unique UNIQUE (username),
    CONSTRAINT users_email_unique UNIQUE (email)
);

-- Case-insensitive uniqueness
CREATE UNIQUE INDEX idx_users_username_lower
    ON users (LOWER(username));

CREATE UNIQUE INDEX idx_users_email_lower
    ON users (LOWER(email));

CREATE INDEX idx_users_created_at
    ON users (created_at);

CREATE INDEX idx_users_status
    ON users (is_suspended, blocked_till);


-- ============================================================
-- GAME
-- ============================================================

CREATE TABLE game (
    game_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL,
    sample_payload JSONB NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT game_name_unique UNIQUE (name)
);

CREATE INDEX idx_game_name
    ON game (name);


-- ============================================================
-- SERIES
-- ============================================================

CREATE TABLE series (
    series_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    game_id UUID NOT NULL,
    player1_id UUID NOT NULL,
    player2_id UUID NOT NULL,

    target_wins INTEGER NOT NULL,

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    CONSTRAINT series_game_fk
        FOREIGN KEY (game_id)
        REFERENCES game (game_id),

    CONSTRAINT series_player1_fk
        FOREIGN KEY (player1_id)
        REFERENCES users (id),

    CONSTRAINT series_player2_fk
        FOREIGN KEY (player2_id)
        REFERENCES users (id),

    CONSTRAINT series_different_players
        CHECK (player1_id <> player2_id),

    CONSTRAINT series_target_wins_positive
        CHECK (target_wins > 0),

    CONSTRAINT series_dates_valid
        CHECK (
            ended_at IS NULL
            OR ended_at >= started_at
        )
);

CREATE INDEX idx_series_game_id
    ON series (game_id);

CREATE INDEX idx_series_player1_id
    ON series (player1_id);

CREATE INDEX idx_series_player2_id
    ON series (player2_id);

CREATE INDEX idx_series_players
    ON series (player1_id, player2_id);

CREATE INDEX idx_series_started_at
    ON series (started_at);

-- Active series
CREATE INDEX idx_series_active
    ON series (started_at)
    WHERE ended_at IS NULL;


-- ============================================================
-- MATCH
-- ============================================================

CREATE TABLE match (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    series_id UUID NOT NULL,

    game_board JSONB NOT NULL DEFAULT '{}'::jsonb,
    player_moves JSONB NOT NULL DEFAULT '[]'::jsonb,

    is_finished BOOLEAN NOT NULL DEFAULT FALSE,

    winner_id UUID,

    played_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    CONSTRAINT match_series_fk
        FOREIGN KEY (series_id)
        REFERENCES series (series_id)
        ON DELETE CASCADE,

    CONSTRAINT match_winner_fk
        FOREIGN KEY (winner_id)
        REFERENCES users (id),

    CONSTRAINT match_dates_valid
        CHECK (
            ended_at IS NULL
            OR ended_at >= played_at
        ),

    CONSTRAINT match_finished_state_valid
        CHECK (
            (is_finished = FALSE AND ended_at IS NULL)
            OR
            (is_finished = TRUE AND ended_at IS NOT NULL)
        )
);

CREATE INDEX idx_match_series_id
    ON match (series_id);

CREATE INDEX idx_match_winner_id
    ON match (winner_id);

CREATE INDEX idx_match_played_at
    ON match (played_at);

CREATE INDEX idx_match_series_played_at
    ON match (series_id, played_at);

-- Active matches
CREATE INDEX idx_match_active
    ON match (series_id)
    WHERE is_finished = FALSE;


COMMIT;