"""WebSocket piyasa veri akışı endpoint'i."""

import json

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket_manager import ws_manager

logger = structlog.get_logger()

router = APIRouter()


@router.websocket("/ws/v1/market/stream")
async def market_stream(websocket: WebSocket):
    """Piyasa verisi WebSocket stream.

    Client mesaj formatı:
        {"action": "subscribe", "channels": ["quote:THYAO", "orderbook:GARAN"]}
        {"action": "unsubscribe", "channels": ["quote:THYAO"]}

    Server mesaj formatı:
        {"channel": "quote:THYAO", "data": {...}}
    """
    await ws_manager.connect(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
                action = message.get("action")
                channels = message.get("channels", [])

                if action == "subscribe":
                    for ch in channels:
                        ws_manager.subscribe(websocket, ch)
                    await ws_manager.send_personal(websocket, {
                        "type": "subscribed",
                        "channels": channels,
                    })

                elif action == "unsubscribe":
                    for ch in channels:
                        ws_manager.unsubscribe(websocket, ch)
                    await ws_manager.send_personal(websocket, {
                        "type": "unsubscribed",
                        "channels": channels,
                    })

            except json.JSONDecodeError:
                await ws_manager.send_personal(websocket, {
                    "type": "error",
                    "message": "Geçersiz JSON formatı",
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
