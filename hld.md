# A lan game of chess and tictactoe with websockets

2 players can play a game of chess. the other player can be an LLM too, even 2 LLM's can play the chess. LLM and human, the difference is unknown to the server

## Components

1. Fastapi websocket: A websocket endpoint where 2 players can connect. This endpoint ensures all the validations for the clients and serve the game. We need persistent connection for the game

2. UI: React UI that renders the board and the game state so that browsers can present the game to the user

3. Auth: A dummy auth with just username, email, password_hash, created_at, is_blocked, blocked_till fields. 

4. Register and login UI: user can register and login, select the game and wait for friends

5. DB: persist games so that user can see what games he played, what moves he made etc

6. LLMs: An LLM application that hits requests to the websocket endpoint, LLM will emulate the human

Making this game to dig deep in websockets, LAN gaming, integrating LLMs in everyday applications. Seperation of application and LLM. Making LLM emulate the user.

## DB Schema initial draft

```
users
-----------
id <pk>
username
password_hash
email
created_at
is_suspended
blocked_till
is_busy

unique username, email

game
------------
game_id pk
name
sample_payload jsonb

series
--------------
series_id pk
game_id fk game
player1_id fk users
player2_id fk users
target_wins
started_at
ended_at

match
----------
match_id pk
series_id fk series
game_board jsonb
player_moves jsonb
is_finished
winner_id fk users
played_at
ended_at

```

## Games

### Game interface

User only needs
1. Send a payload
2. receive a response
3. know if the game is finished
4. Who won

An interface with

class Game:
    def make_move()
    def add_player()
    def get_result()
    def get_board()
    def get_player_stats()

get_result should return a status instead of plain strings and responses

class GetResultEnum:
   ongoing
   finished
   draw

make_move response should also be structured

class MakeMoveResponse:
    match_id
    player_1_id
    player_2_id
    board_state
    move_made_by

class AddPlayer:
    player_id
    message

define common exceptions

1. when we try to add a player, it fails
2. when board updation fails

identify more

keep db away from the game object so that game can be tested independently of api

each game is different, tney have different rules, don't force abstracitons. keep the above interface so that API can interact.

keep a generic dataclass call it payload or action, it is different for each game

### Tic tac toe

Tic tac toe is very simple. 1 player gets x and other o. continuous 3 x means x won, the 3 x can be continious in row, col or diag. 

Keep the game interface intact, write one more object TicTacToeGameValidations, you need to ensure how to update the board, check if game is finished etc. 

### chess

this is very complex game, use python-chess library for all the validations. keep the game interface for api interaction