import asyncio
import json

import websockets
import argparse
import httpx

LOGIN_URL = "http://127.0.0.1:8000/v1/auth/login"
WS_URL = "ws://127.0.0.1:8000/v1/play/join"


def get_args():
    args = argparse.ArgumentParser(description="Websocket client")
    args.add_argument("--username", required=True)
    args.add_argument("--password", required=True)
    parser = args.parse_args()
    return parser


async def login(username, password):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            url=LOGIN_URL, json={"identifier": username, "password": password}
        )
    return res.json()["access_token"]


async def send(ws):
    while True:
        message = await asyncio.to_thread(
            input,
            "## ",
        )
        await ws.send(message)


def print_board(board):
    for i, row in enumerate(board):
        print(" | ".join(cell or " " for cell in row))

        if i < len(board) - 1:
            print("---+---+---")

async def recv(ws):
    async for message in ws:
        data = json.loads(message)
        event = data["event"]

        if event in ("board_update", "finished"):
            
            print("\033[H\033[J", end="")
            print_board(data["board"])

        if event == "finished":
            if data["winner"] is None:
                print("\nIt's a draw!")
            else:
                print(f"\n Winner: {data['winner']}")

            print(f"Winning line: {data['win_state']}")


async def ws_connect(token: str):
    uri = f"{WS_URL}?token={token}"
    async with websockets.connect(uri) as ws:
        await asyncio.gather(send(ws), recv(ws))


async def main():
    args = get_args()
    token = await login(args.username, args.password)
    await ws_connect(token)


if __name__ == "__main__":
    asyncio.run(main())
