"""WebSocket routes for real-time updates."""

import json
import logging
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState

from ...core.extractor import ImageContextExtractor
from ...config.settings import get_config

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "general": set(),
            "processing": set(),
            "search": set(),
            "duplicates": set()
        }
    
    async def connect(self, websocket: WebSocket, channel: str = "general"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket connected to channel '{channel}'. Total connections: {len(self.active_connections[channel])}")
    
    def disconnect(self, websocket: WebSocket, channel: str = "general"):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"WebSocket disconnected from channel '{channel}'. Total connections: {len(self.active_connections[channel])}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_channel(self, message: dict, channel: str = "general"):
        if channel in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[channel]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(json.dumps(message))
                    else:
                        disconnected.add(connection)
                except Exception as e:
                    logger.error(f"Error broadcasting to {channel}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[channel].discard(conn)
    
    async def broadcast_to_all(self, message: dict):
        for channel in self.active_connections:
            await self.broadcast_to_channel(message, channel)


manager = ConnectionManager()


def get_extractor() -> ImageContextExtractor:
    """Dependency to get the extractor instance."""
    config = get_config()
    return ImageContextExtractor(config)


@router.websocket("/ws")
async def websocket_general(websocket: WebSocket):
    """General WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, "general")
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Connected to general updates channel",
            "timestamp": asyncio.get_event_loop().time()
        }, websocket)
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": asyncio.get_event_loop().time()
                }, websocket)
            
            elif message_data.get("type") == "subscribe":
                # Handle channel subscription
                channel = message_data.get("channel", "general")
                await manager.connect(websocket, channel)
                await manager.send_personal_message({
                    "type": "subscribed",
                    "channel": channel,
                    "message": f"Subscribed to {channel} channel"
                }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "general")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "general")


@router.websocket("/ws/processing")
async def websocket_processing(websocket: WebSocket):
    """WebSocket endpoint for processing updates."""
    await manager.connect(websocket, "processing")
    
    try:
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Connected to processing updates channel",
            "timestamp": asyncio.get_event_loop().time()
        }, websocket)
        
        while True:
            data = await websocket.receive_text()
            # Echo back for now (can be extended for specific processing commands)
            await manager.send_personal_message({
                "type": "echo",
                "data": data,
                "timestamp": asyncio.get_event_loop().time()
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "processing")
    except Exception as e:
        logger.error(f"Processing WebSocket error: {e}")
        manager.disconnect(websocket, "processing")


@router.websocket("/ws/search")
async def websocket_search(websocket: WebSocket):
    """WebSocket endpoint for search updates."""
    await manager.connect(websocket, "search")
    
    try:
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Connected to search updates channel",
            "timestamp": asyncio.get_event_loop().time()
        }, websocket)
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle live search requests
            if message_data.get("type") == "live_search":
                query = message_data.get("query", "")
                if len(query) >= 3:  # Minimum query length
                    try:
                        extractor = get_extractor()
                        results = extractor.search_similar_images(query, n_results=5)
                        
                        await manager.send_personal_message({
                            "type": "search_results",
                            "query": query,
                            "results": results[:3],  # Limit for real-time
                            "total_results": len(results),
                            "timestamp": asyncio.get_event_loop().time()
                        }, websocket)
                        
                    except Exception as e:
                        await manager.send_personal_message({
                            "type": "search_error",
                            "query": query,
                            "error": str(e),
                            "timestamp": asyncio.get_event_loop().time()
                        }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "search")
    except Exception as e:
        logger.error(f"Search WebSocket error: {e}")
        manager.disconnect(websocket, "search")


# Helper functions to send updates from other parts of the application

async def notify_image_processed(image_path: str, image_id: str, processing_time: float):
    """Notify WebSocket clients that an image has been processed."""
    message = {
        "type": "image_processed",
        "image_path": image_path,
        "image_id": image_id,
        "processing_time": processing_time,
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.broadcast_to_channel(message, "processing")
    await manager.broadcast_to_channel(message, "general")


async def notify_directory_progress(directory_path: str, progress: float, current_file: str, stats: dict):
    """Notify WebSocket clients about directory processing progress."""
    message = {
        "type": "directory_progress",
        "directory_path": directory_path,
        "progress": progress,
        "current_file": current_file,
        "stats": stats,
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.broadcast_to_channel(message, "processing")
    await manager.broadcast_to_channel(message, "general")


async def notify_duplicates_found(duplicate_groups: list, total_duplicates: int):
    """Notify WebSocket clients about duplicate detection results."""
    message = {
        "type": "duplicates_found",
        "duplicate_groups": len(duplicate_groups),
        "total_duplicates": total_duplicates,
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.broadcast_to_channel(message, "duplicates")
    await manager.broadcast_to_channel(message, "general")


async def notify_system_status(status: dict):
    """Notify WebSocket clients about system status changes."""
    message = {
        "type": "system_status",
        "status": status,
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.broadcast_to_all(message)


# Endpoint to get WebSocket connection statistics
@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    stats = {}
    total_connections = 0
    
    for channel, connections in manager.active_connections.items():
        active_count = len([conn for conn in connections if conn.client_state == WebSocketState.CONNECTED])
        stats[channel] = active_count
        total_connections += active_count
    
    return {
        "total_connections": total_connections,
        "channels": stats,
        "timestamp": asyncio.get_event_loop().time()
    }