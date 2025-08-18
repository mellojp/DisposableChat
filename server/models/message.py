from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    id: str
    type: str  # 'chat', 'user_joined', 'user_left', 'system'
    user: str
    message: str
    timestamp: datetime
    room_id: str

class MessageCreate(BaseModel):
    type: str
    message: str

class MessageResponse(BaseModel):
    id: str
    type: str
    user: str
    message: str
    timestamp: datetime