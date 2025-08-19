
# Disposable Chat API

A lightweight API for **anonymous, real-time conversations** in **temporary chat rooms**.  
Built with **FastAPI** and **WebSockets**, it enables **ephemeral communication** for web, mobile, and desktop apps.  

---

## ✨ Features

- **Session-based authentication** – no permanent accounts, only temporary `session_id`.
- **Temporary rooms** – created on demand, deleted after inactivity.
- **Real-time messaging** – powered by WebSockets (low-latency, bidirectional).
- **Recent messages** – get the last few messages when joining a room.
- **Typing indicators** – see when someone is typing.
- **Cross-platform** – works with any client that supports REST + WebSockets.

---

## 🚀 Local Setup

### Requirements
- Python **3.8+**
- `pip` + `venv`

### 1. Clone repo
```bash
git clone <REPOSITORY_URL>
cd disposable-chat
```

### 2. Create virtual env
**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**
```bash
python -m venv venv
.
env\Scripts ctivate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run server
```bash
uvicorn main:app --reload
```

➡ API available at: **http://127.0.0.1:8000**

---

## 🔑 API Flow

1. **Create session (REST)** → get `session_id`  
2. **Join or create room (REST)** → get `room_id`  
3. **Connect via WebSocket** with `session_id` + `room_id`  

---

## 🌐 WebSocket Connection

**URL format:**
```
ws://[host]/ws/[room_id]?session_id=[your_session_id]
```

**Example:**
```
ws://127.0.0.1:8000/ws/a1b2c3d4e5?session_id=a1b2c3d4-e5f6-7890-1234-567890abcdef
```

| Part        | Description                          | Example           |
|-------------|--------------------------------------|-------------------|
| protocol    | `ws` (non-secure) / `wss` (secure)   | ws                |
| host        | Server domain or IP                  | 127.0.0.1:8000    |
| path        | `/ws/[room_id]`                      | /ws/a1b2c3d4e5    |
| query param | `session_id` token                   | session_id=abc123 |

---

## 📩 Message Format

Messages use **JSON**.

### Client → Server
**Chat message**
```json
{ "type": "chat", "message": "Hello world!" }
```

**Typing indicator**
```json
{ "type": "typing" }
```

### Server → Client
**Chat message**
```json
{
  "id": "msg-uuid",
  "type": "chat",
  "user": "username",
  "message": "Content here",
  "timestamp": "2025-08-19T13:45:00.123456",
  "room_id": "a1b2c3d4e5"
}
```

**User join/leave**
```json
{
  "id": "notif-uuid",
  "type": "user_joined",
  "user": "username",
  "message": "username has joined",
  "timestamp": "...",
  "room_id": "a1b2c3d4e5"
}
```

**Typing indicator**
```json
{ "type": "typing", "user": "username" }
```

---

## 💻 Example Client (JS)
```javascript
let roomId = "a1b2c3d4e5";
let sessionId = "a1b2c3d4-e5f6-7890-1234-567890abcdef";
let url = `ws://localhost:8000/ws/${roomId}?session_id=${sessionId}`;

let socket = new WebSocket(url);

socket.onopen = () => {
  socket.send(JSON.stringify({ type: "chat", message: "Hello!" }));
};

socket.onmessage = (event) => {
  let data = JSON.parse(event.data);
  if (data.type === "chat") console.log(`${data.user}: ${data.message}`);
  if (data.type === "user_joined") console.log(`${data.user} joined`);
  if (data.type === "typing") console.log(`${data.user} is typing...`);
};

socket.onclose = () => console.log("Disconnected");
socket.onerror = (err) => console.error("Error:", err);
```

---

