from pydantic import BaseModel
from datetime import datetime

class UserSession(BaseModel):
    session_id: str
    username: str
    joined_rooms: list[str] = []
    created_at: datetime
    last_activity: datetime

class CreateSessionRequest(BaseModel):
    username: str

class SessionResponse(BaseModel):
    session_id: str
    username: str
    joined_rooms: list[str]