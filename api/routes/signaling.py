"""
WebSocket Signaling Server for Video Calls & Online Classroom
=============================================================
Manages rooms, participants, and relays WebRTC signaling messages
(SDP offers/answers, ICE candidates) + classroom events
(chat, hand raise, mute, notes, class ended).
"""
import json
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["Signaling"])

# ── Room State ───────────────────────────────
# rooms[room_id] = set of WebSocket connections
rooms: Dict[str, Set[WebSocket]] = {}

# user_info[ws_id] = {userId, userName, role, roomId}
user_info: Dict[int, dict] = {}


@router.websocket("/ws/signaling")
async def signaling_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_id = id(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")

            # ────────────────────────────────
            #  JOIN ROOM
            # ────────────────────────────────
            if msg_type == "join":
                room_id = msg.get("roomId", "")
                user_id = msg.get("userId", "")
                user_name = msg.get("userName", "User")
                role = msg.get("role", "student")

                if room_id not in rooms:
                    rooms[room_id] = set()
                rooms[room_id].add(websocket)

                user_info[ws_id] = {
                    "userId": user_id,
                    "userName": user_name,
                    "role": role,
                    "roomId": room_id,
                }

                # Notify others in room that someone joined
                await _broadcast(room_id, {
                    "type": "participant_joined",
                    "userId": user_id,
                    "userName": user_name,
                    "role": role,
                }, exclude=websocket)

                # Send existing participants to the new joiner
                for other_ws in rooms[room_id]:
                    other_id = id(other_ws)
                    if other_id != ws_id and other_id in user_info:
                        info = user_info[other_id]
                        await _send(websocket, {
                            "type": "participant_joined",
                            "userId": info["userId"],
                            "userName": info["userName"],
                            "role": info["role"],
                        })

                print(f"[ROOM {room_id}] {user_name} ({role}) joined. "
                      f"Total: {len(rooms[room_id])}")

            # ────────────────────────────────
            #  LEAVE ROOM
            # ────────────────────────────────
            elif msg_type == "leave":
                await _handle_leave(websocket, ws_id)

            # ────────────────────────────────
            #  WEBRTC SIGNALING (relay to room)
            # ────────────────────────────────
            elif msg_type in ("offer", "answer", "candidate", "hangup"):
                info = user_info.get(ws_id, {})
                room_id = info.get("roomId", "")
                if room_id:
                    await _broadcast(room_id, msg, exclude=websocket)

            # ────────────────────────────────
            #  CHAT MESSAGE (relay to room)
            # ────────────────────────────────
            elif msg_type == "chat":
                info = user_info.get(ws_id, {})
                room_id = info.get("roomId", "")
                if room_id:
                    await _broadcast(room_id, msg, exclude=websocket)

            # ────────────────────────────────
            #  CLASSROOM EVENTS (relay)
            # ────────────────────────────────
            elif msg_type in ("mute_student", "mute_all", "hand_raise",
                              "notes_shared", "class_ended", "whiteboard"):
                info = user_info.get(ws_id, {})
                room_id = info.get("roomId", "")
                if room_id:
                    await _broadcast(room_id, msg, exclude=websocket)

    except WebSocketDisconnect:
        await _handle_leave(websocket, ws_id)
    except Exception as e:
        print(f"[WS ERROR] {e}")
        await _handle_leave(websocket, ws_id)


# ── Helpers ──────────────────────────────────

async def _handle_leave(websocket: WebSocket, ws_id: int):
    """Remove user from room and notify others."""
    info = user_info.pop(ws_id, None)
    if info:
        room_id = info["roomId"]
        if room_id in rooms:
            rooms[room_id].discard(websocket)
            await _broadcast(room_id, {
                "type": "participant_left",
                "userId": info["userId"],
                "userName": info["userName"],
            })
            print(f"[ROOM {room_id}] {info['userName']} left. "
                  f"Remaining: {len(rooms[room_id])}")
            if not rooms[room_id]:
                del rooms[room_id]
                print(f"[ROOM {room_id}] Room closed (empty)")


async def _broadcast(room_id: str, message: dict, exclude: WebSocket = None):
    """Send a message to all connections in a room except the excluded one."""
    if room_id not in rooms:
        return
    payload = json.dumps(message)
    dead = set()
    for ws in rooms[room_id]:
        if ws is exclude:
            continue
        try:
            await ws.send_text(payload)
        except Exception:
            dead.add(ws)
    for ws in dead:
        rooms[room_id].discard(ws)


async def _send(websocket: WebSocket, message: dict):
    """Send a message to a single WebSocket connection."""
    try:
        await websocket.send_text(json.dumps(message))
    except Exception:
        pass


# ── REST endpoint: list active rooms ─────────
@router.get("/rooms", tags=["Signaling"])
async def list_rooms():
    """List all active classroom rooms with participant counts."""
    result = []
    for room_id, connections in rooms.items():
        participants = []
        for ws in connections:
            info = user_info.get(id(ws))
            if info:
                participants.append({
                    "userId": info["userId"],
                    "userName": info["userName"],
                    "role": info["role"],
                })
        result.append({
            "roomId": room_id,
            "participantCount": len(connections),
            "participants": participants,
        })
    return {"rooms": result, "totalRooms": len(result)}
