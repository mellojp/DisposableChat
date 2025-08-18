import uuid
from datetime import datetime, timedelta
from ..models.session import UserSession

class SessionManager:
    def __init__(self):
        self.sessions: dict[str, UserSession] = {}
        self.username_to_session: dict[str, str] = {}
        self.SESSION_TTL_HOURS = 24

    def create_session(self, username: str) -> str:
        # Remove sessão anterior se existir
        if username in self.username_to_session:
            old_session_id = self.username_to_session[username]
            self.remove_session(old_session_id)

        session_id = str(uuid.uuid4())
        session = UserSession(
            session_id=session_id,
            username=username,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.sessions[session_id] = session
        self.username_to_session[username] = session_id
        return session_id

    def get_session(self, session_id: str) -> UserSession | None:
        session = self.sessions.get(session_id)
        if session and self._is_session_valid(session):
            session.last_activity = datetime.now()
            return session
        elif session:
            self.remove_session(session_id)
        return None

    def add_room_to_session(self, session_id: str, room_id: str):
        session = self.get_session(session_id)
        if session and room_id not in session.joined_rooms:
            session.joined_rooms.append(room_id)

    def remove_room_from_session(self, session_id: str, room_id: str):
        session = self.get_session(session_id)
        if session and room_id in session.joined_rooms:
            session.joined_rooms.remove(room_id)

    def _is_session_valid(self, session: UserSession) -> bool:
        return datetime.now() - session.last_activity < timedelta(hours=self.SESSION_TTL_HOURS)

    def remove_session(self, session_id: str):
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.username in self.username_to_session:
                del self.username_to_session[session.username]
            del self.sessions[session_id]

    def cleanup_expired_sessions(self):
        """Remove sessões expiradas - pode ser chamado periodicamente"""
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if not self._is_session_valid(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.remove_session(session_id)

session_manager = SessionManager()