
# Live Chat API

A lightweight API for **anonymous, real-time conversations** in **temporary chat rooms**.  
Built with **FastAPI** and **WebSockets**, it enables **chat communication** for web, mobile, and desktop apps.  

---

## Features

- **Session-based authentication** – no permanent accounts, only temporary `session_id`.
- **Temporary rooms** – created on demand, deleted after inactivity.
- **Real-time messaging** – powered by WebSockets (low-latency, bidirectional).
- **Recent messages** – get the last few messages when joining a room.
- **Typing indicators** – see when someone is typing.
- **Cross-platform** – works with any client that supports REST + WebSockets.

---

## API Utilization Protocol

1. Authentication (via HTTP): It is necessary to execute a REST request to create a session, from which a session identifier `session_id` will be obtained to function as an authorization token.

2. Room Acquisition (via HTTP): The session token must be utilized to request the creation of or entry into a chat room, resulting in the acquisition of a room identifier `room_id`.

3. Connection (via WebSocket): The session and room identifiers are then employed to establish the real-time communication link.

Full API documentation avaliable in: https://disposable-chat.onrender.com/docs

---

## WebSocket Connection

### Preconditions for Connection Establishment

For a WebSocket connection to be successfully initiated, the client entity must have the identifiers acquired via **API requests**:

`room_id`: The unique identifier for the chat room.

`session_id`: An active user session token, which serves as the authentication credential for the connection.

The absence of a valid `session_id` will result in the server's refusal of the connection.

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

## Message Format

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

## Example Client (JS)
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

