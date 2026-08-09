import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from websocket_manager import EventType, WebSocketEvent
from runtime import ws_manager
from structured_logger import get_logger

router = APIRouter()
logger = get_logger("websocket")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())

    if await ws_manager.connect(websocket, client_id):
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                msg_type = message.get("type")

                if msg_type == "ping":
                    await ws_manager.send_personal_message(
                        WebSocketEvent(EventType.SYSTEM_STATUS, {"message": "pong"}),
                        client_id
                    )

                elif msg_type == "subscribe":
                    event_types = message.get("events", [])
                    types = [EventType(t) for t in event_types if t in EventType.__members__]
                    ws_manager.subscribe(client_id, types)

                elif msg_type == "unsubscribe":
                    event_types = message.get("events", [])
                    types = [EventType(t) for t in event_types if t in EventType.__members__]
                    ws_manager.unsubscribe(client_id, types)

        except WebSocketDisconnect:
            await ws_manager.disconnect(client_id)
        except Exception as e:
            logger.error(f"[WS] Error for client {client_id}: {e}")
            await ws_manager.disconnect(client_id)


@router.get("/api/ws/stats")
async def get_websocket_stats():
    return ws_manager.get_stats()
