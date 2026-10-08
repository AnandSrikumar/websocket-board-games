import asyncio

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


async def recv(ws):
    async for message in ws:
        print(f"\n>> {message}")


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
