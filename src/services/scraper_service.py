import json
import ssl
import time

import websockets

from src.core.auth.crypto import (
    decrypt_payload,
    generate_challenge,
    generate_nonce,
    generate_timestamp,
    solve_pow,
)
from src.core.http.client import HttpClient
from src.core.http.websocket_client import WebSocketClient


class ScraperService:
    """
    Orchestrates login flows (easy / hard / extreme).
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        http_client: HttpClient,
        ws_client: WebSocketClient,
    ):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._http = http_client
        self._ws = ws_client

    async def run(self, level: str = "extreme") -> dict:
        runners = {
            "easy": self._run_easy,
            "hard": self._run_hard,
            "extreme": self._run_extreme,
        }
        if level not in runners:
            raise ValueError(f"Invalid level '{level}'. Choose from: {list(runners)}")
        return await runners[level]()

    async def _run_easy(self) -> dict:
        data = await self._http.post(
            f"{self._base_url}/api/easy/login",
            {"username": self._username, "password": self._password},
        )
        if not data.get("success"):
            raise RuntimeError(f"EASY login failed: {data}")
        return data

    async def _run_hard(self) -> dict:
        timestamp = generate_timestamp()
        nonce = generate_nonce()
        challenge = generate_challenge(timestamp, nonce)

        data = await self._http.post(
            f"{self._base_url}/api/hard/login",
            {
                "username": self._username,
                "password": self._password,
                "timestamp": timestamp,
                "nonce": nonce,
                "challenge": challenge,
            },
        )
        if not data.get("success"):
            raise RuntimeError(f"HARD login failed: {data}")
        return {"token": data["auth_token"]}

    async def _run_extreme(self) -> dict:
        init_data = await self._http.post_empty(f"{self._base_url}/api/extreme/init")
        session_id = init_data["session_id"]
        ws_ticket = init_data["ws_ticket"]
        print(f"SESSION: {session_id}")

        ws_url = f"{self._base_url.replace('https', 'wss')}/ws?ticket={ws_ticket}&session_id={session_id}"
        intermediate_token = await self._exchange_pow_over_ws(ws_url)

        verify_data = await self._http.post(
            f"{self._base_url}/api/extreme/verify-token",
            {"session_id": session_id, "intermediate_token": intermediate_token},
        )
        otp = decrypt_payload(session_id, verify_data["encrypted_payload"])["otp"]

        final_data = await self._http.post(
            f"{self._base_url}/api/extreme/complete",
            {
                "session_id": session_id,
                "otp": otp,
                "username": self._username,
                "password": self._password,
            },
        )
        if not final_data.get("success"):
            raise RuntimeError(f"EXTREME failed: {final_data}")
        return final_data

    async def _exchange_pow_over_ws(self, ws_url: str) -> str:
        """Connect via WebSocket, solve the POW challenge, return the intermediate token."""
        ssl_ctx = ssl.create_default_context(cafile=self._ws.ca_path)
        ssl_ctx.load_cert_chain(self._ws.cert_path)

        async with websockets.connect(ws_url, ssl=ssl_ctx) as ws:
            challenge = json.loads(await ws.recv())

            start = time.time()
            nonce = solve_pow(challenge["prefix"], challenge["difficulty"])
            print(f"POW solved in {time.time() - start:.2f}s")

            await ws.send(json.dumps({"nonce": nonce}))
            result = json.loads(await ws.recv())

        return result["intermediate_token"]