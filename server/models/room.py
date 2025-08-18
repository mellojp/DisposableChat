from pydantic import BaseModel
from datetime import datetime

class Room(BaseModel):
    room_id: str
    created_at: datetime
    last_activity: datetime
    active_users: list[str] = []

class RoomResponse(BaseModel):
    room_id: str
    exists: bool
    user_count: int = 0

class RoomListResponse(BaseModel):
    rooms: list[str]