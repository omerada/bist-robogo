# Source: Doc 07 §15.1 — WebSocket Yönetimi
"""WebSocket bağlantı yöneticisi — channel-based pub/sub."""

import json
from typing import Any

import structlog
from fastapi import WebSocket

logger = structlog.get_logger()


class WebSocketManager:
    """WebSocket bağlantılarını channel bazlı yönetir.

    Kanallar:
    - quote:{symbol} → Fiyat güncellemeleri
    - orderbook:{symbol} → Order book güncellemeleri
    - signal → Strateji sinyalleri
    - notification:{user_id} → Kullanıcı bildirimleri
    """

    def __init__(self) -> None:
        self.channels: dict[str, set[WebSocket]] = {}
        self.connections: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket) -> None:
        """WebSocket bağlantısını kabul et."""
        await websocket.accept()
        self.connections[websocket] = set()
        logger.info("ws_connected", client=id(websocket))

    def disconnect(self, websocket: WebSocket) -> None:
        """WebSocket bağlantısını kaldır ve tüm kanallardan çıkar."""
        channels = self.connections.pop(websocket, set())
        for channel in channels:
            self.channels.get(channel, set()).discard(websocket)
            if not self.channels.get(channel):
                self.channels.pop(channel, None)
        logger.info("ws_disconnected", client=id(websocket))

    def subscribe(self, websocket: WebSocket, channel: str) -> None:
        """WebSocket'i bir kanala abone et."""
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(websocket)
        self.connections[websocket].add(channel)

    def unsubscribe(self, websocket: WebSocket, channel: str) -> None:
        """WebSocket'i bir kanaldan çıkar."""
        self.channels.get(channel, set()).discard(websocket)
        self.connections.get(websocket, set()).discard(channel)

    async def broadcast(self, channel: str, data: dict[str, Any]) -> None:
        """Bir kanaldaki tüm bağlantılara mesaj gönder."""
        message = json.dumps({"channel": channel, "data": data})
        dead_connections: list[WebSocket] = []

        for ws in self.channels.get(channel, set()):
            try:
                await ws.send_text(message)
            except Exception:
                dead_connections.append(ws)

        for ws in dead_connections:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        """Tek bir bağlantıya mesaj gönder."""
        await websocket.send_json(data)


# Singleton instance
ws_manager = WebSocketManager()
