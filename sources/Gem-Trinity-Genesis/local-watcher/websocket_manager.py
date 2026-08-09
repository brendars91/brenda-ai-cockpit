"""
WebSocket Manager v2.0 - Real-time Updates
Centralized WebSocket connection management for Gem-Trinity Genesis.
"""
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
import json
import asyncio
import logging
from datetime import datetime, timezone
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """Types of events that can be broadcast"""
    # Builder events
    BUILDER_QUEUED = "builder.queued"
    BUILDER_STARTED = "builder.started"
    BUILDER_PROGRESS = "builder.progress"
    BUILDER_COMPLETED = "builder.completed"
    BUILDER_FAILED = "builder.failed"

    # Architect events
    ARCHITECT_STARTED = "architect.started"
    ARCHITECT_COMPLETED = "architect.completed"
    ARCHITECT_FAILED = "architect.failed"

    # Engine events
    ENGINE_STARTED = "engine.started"
    ENGINE_LOG = "engine.log"
    ENGINE_COMPLETED = "engine.completed"
    ENGINE_FAILED = "engine.failed"

    # System events
    SYSTEM_STATUS = "system.status"
    SYSTEM_METRICS = "system.metrics"
    SYSTEM_ERROR = "system.error"

    # Workflow events
    WORKFLOW_STAGE_CHANGE = "workflow.stage_change"
    WORKFLOW_COMPLETED = "workflow.completed"

class WebSocketEvent:
    """Structured event for WebSocket broadcasting"""

    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        event_id: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or asyncio.get_event_loop().time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "event_id": self.event_id,
            "type": self.event_type.value,
            "timestamp": self.timestamp,
            "data": self.data
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts events.

    Features:
    - Connection lifecycle management
    - Event broadcasting to all clients
    - Targeted messaging to specific clients
    - Automatic reconnection handling
    - Connection statistics
    """

    def __init__(self):
        # Active connections: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # Connection metadata: {client_id: metadata}
        self.connection_metadata: Dict[str, Dict] = {}

        # Subscriptions: {client_id: set of event_types}
        self.subscriptions: Dict[str, Set[EventType]] = {}

        # Statistics
        self.stats = {
            "total_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0
        }

        # Background task for connection health checks
        self._health_check_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, client_id: str) -> bool:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection
            client_id: Unique identifier for the client

        Returns:
            True if connection successful, False otherwise
        """
        try:
            await websocket.accept()

            self.active_connections[client_id] = websocket
            self.connection_metadata[client_id] = {
                "connected_at": asyncio.get_event_loop().time(),
                "last_ping": asyncio.get_event_loop().time(),
                "ip_address": websocket.client.host if websocket.client else None
            }
            self.subscriptions[client_id] = set()  # Subscribe to all by default

            self.stats["total_connections"] += 1

            logger.info(f"[WS] Client connected: {client_id}")

            # Send welcome message
            await self.send_personal_message(
                WebSocketEvent(
                    EventType.SYSTEM_STATUS,
                    {"message": "Connected to Gem-Trinity Genesis", "client_id": client_id}
                ),
                client_id
            )

            # Start health check if not running
            if self._health_check_task is None:
                self._health_check_task = asyncio.create_task(self._health_check_loop())

            return True

        except Exception as e:
            logger.error(f"[WS] Connection failed for {client_id}: {e}")
            self.stats["errors"] += 1
            return False

    async def disconnect(self, client_id: str):
        """
        Disconnect and clean up a client connection.

        Args:
            client_id: Client to disconnect
        """
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.close()
            except Exception:
                pass  # Connection might already be closed

            del self.active_connections[client_id]
            del self.connection_metadata[client_id]
            del self.subscriptions[client_id]

            logger.info(f"[WS] Client disconnected: {client_id}")

    async def send_personal_message(self, event: WebSocketEvent, client_id: str):
        """
        Send an event to a specific client.

        Args:
            event: Event to send
            client_id: Target client
        """
        if client_id not in self.active_connections:
            logger.warning(f"[WS] Cannot send to unknown client: {client_id}")
            return

        try:
            websocket = self.active_connections[client_id]
            await websocket.send_text(event.to_json())
            self.stats["messages_sent"] += 1

        except WebSocketDisconnect:
            logger.warning(f"[WS] Client disconnected during send: {client_id}")
            await self.disconnect(client_id)
        except Exception as e:
            logger.error(f"[WS] Send failed to {client_id}: {e}")
            self.stats["errors"] += 1

    async def broadcast(self, event: WebSocketEvent, event_type_filter: Optional[EventType] = None):
        """
        Broadcast an event to all connected clients.

        Args:
            event: Event to broadcast
            event_type_filter: Only send to clients subscribed to this event type
        """
        if not self.active_connections:
            return

        # Get clients to send to
        target_clients = list(self.active_connections.keys())

        if event_type_filter:
            target_clients = [
                client_id for client_id in target_clients
                if event_type_filter in self.subscriptions.get(client_id, set())
                or not self.subscriptions.get(client_id)  # No filter = all events
            ]

        # Send to all target clients concurrently
        tasks = [
            self.send_personal_message(event, client_id)
            for client_id in target_clients
        ]

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_builder_progress(self, build_id: str, progress: int, stage: str):
        """
        Convenience method for builder progress updates.

        Args:
            build_id: Build ID
            progress: Progress percentage (0-100)
            stage: Current stage description
        """
        event = WebSocketEvent(
            EventType.BUILDER_PROGRESS,
            {
                "build_id": build_id,
                "progress": progress,
                "stage": stage
            }
        )
        await self.broadcast(event)

    async def broadcast_workflow_stage(self, workflow_id: str, stage: str, status: str):
        """
        Convenience method for workflow stage changes.

        Args:
            workflow_id: Workflow/payload ID
            stage: Current stage (architecting, building, engine)
            status: Status (started, completed, failed)
        """
        event = WebSocketEvent(
            EventType.WORKFLOW_STAGE_CHANGE,
            {
                "workflow_id": workflow_id,
                "stage": stage,
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        )
        await self.broadcast(event)

    async def broadcast_system_metrics(self, metrics: Dict[str, Any]):
        """
        Convenience method for system metrics updates.

        Args:
            metrics: Metrics dictionary
        """
        event = WebSocketEvent(
            EventType.SYSTEM_METRICS,
            metrics
        )
        await self.broadcast(event)

    def subscribe(self, client_id: str, event_types: List[EventType]):
        """
        Subscribe a client to specific event types.

        Args:
            client_id: Client ID
            event_types: List of event types to subscribe to
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(event_types)
            logger.info(f"[WS] Client {client_id} subscribed to {[e.value for e in event_types]}")

    def unsubscribe(self, client_id: str, event_types: List[EventType]):
        """
        Unsubscribe a client from specific event types.

        Args:
            client_id: Client ID
            event_types: List of event types to unsubscribe from
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].difference_update(event_types)
            logger.info(f"[WS] Client {client_id} unsubscribed from {[e.value for e in event_types]}")

    async def _health_check_loop(self):
        """Background task to check connection health"""
        while self.active_connections:
            try:
                # Check each connection
                for client_id in list(self.active_connections.keys()):
                    try:
                        websocket = self.active_connections[client_id]

                        # Send ping
                        await websocket.send_json({"type": "ping", "timestamp": asyncio.get_event_loop().time()})

                        # Update last ping time
                        if client_id in self.connection_metadata:
                            self.connection_metadata[client_id]["last_ping"] = asyncio.get_event_loop().time()

                    except Exception:
                        # Connection dead, remove it
                        await self.disconnect(client_id)

                # Wait before next check
                await asyncio.sleep(30)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[WS] Health check error: {e}")
                await asyncio.sleep(30)

        self._health_check_task = None

    def get_stats(self) -> Dict[str, Any]:
        """Get connection manager statistics"""
        return {
            **self.stats,
            "active_connections": len(self.active_connections),
            "connection_details": {
                client_id: {
                    "connected_at": metadata.get("connected_at"),
                    "last_ping": metadata.get("last_ping"),
                    "ip_address": metadata.get("ip_address")
                }
                for client_id, metadata in self.connection_metadata.items()
            }
        }

    async def cleanup(self):
        """Cleanup all connections and stop background tasks"""
        # Disconnect all clients
        for client_id in list(self.active_connections.keys()):
            await self.disconnect(client_id)

        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        logger.info("[WS] Connection manager cleanup complete")

# Singleton instance
_manager: Optional[ConnectionManager] = None

def get_websocket_manager() -> ConnectionManager:
    """Get singleton WebSocket manager instance"""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager
