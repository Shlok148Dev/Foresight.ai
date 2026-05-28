"""
Foresight — WebSocket Hub
==========================
Phase 2D: Real-time signal streaming via WebSocket.
Clients subscribe to `/ws/signals` or `/ws/trends`.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("foresight.ws")

router = APIRouter(tags=["realtime"])


class ConnectionHub:
    """Thread-safe WebSocket connection manager with topic support."""

    def __init__(self) -> None:
        # topic → set of connected sockets
        self._channels: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, topic: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            if topic not in self._channels:
                self._channels[topic] = set()
            self._channels[topic].add(ws)
        logger.info("WS connected: topic=%s total=%d", topic, self._count())

    async def unsubscribe(self, topic: str, ws: WebSocket) -> None:
        async with self._lock:
            self._channels.get(topic, set()).discard(ws)
        logger.info("WS disconnected: topic=%s total=%d", topic, self._count())

    async def broadcast(self, topic: str, payload: dict) -> None:
        """Send payload to all subscribers of a topic."""
        message = json.dumps(payload)
        dead: list[WebSocket] = []
        for ws in list(self._channels.get(topic, set())):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        # Clean up stale connections
        async with self._lock:
            for ws in dead:
                self._channels.get(topic, set()).discard(ws)

    async def broadcast_all(self, payload: dict) -> None:
        """Broadcast to every connected client."""
        for topic in list(self._channels):
            await self.broadcast(topic, payload)

    def _count(self) -> int:
        return sum(len(v) for v in self._channels.values())


hub = ConnectionHub()


# ── Endpoints ─────────────────────────────────────────────────────


@router.websocket("/ws/signals")
async def ws_signals(websocket: WebSocket) -> None:
    """Real-time signal feed."""
    await hub.subscribe("signals", websocket)
    try:
        await websocket.send_json({"type": "connected", "channel": "signals"})
        while True:
            # Keep-alive: echo pings from client
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await hub.unsubscribe("signals", websocket)


@router.websocket("/ws/trends")
async def ws_trends(websocket: WebSocket) -> None:
    """Real-time trend detection feed."""
    await hub.subscribe("trends", websocket)
    try:
        await websocket.send_json({"type": "connected", "channel": "trends"})
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await hub.unsubscribe("trends", websocket)
