import uuid

class RoomManager:
    def __init__(self):
        self.active_rooms: set[str] = set()
        print("RoomManager inicializado.")

    def create_room(self) -> str:
        """Cria uma nova sala, adiciona à lista de ativas e retorna seu ID."""
        room_id = str(uuid.uuid4().hex)[:10]
        self.active_rooms.add(room_id)
        print(f"Sala criada: {room_id}. Salas ativas: {self.active_rooms}")
        return room_id

    def list_rooms(self) -> list[str]:
        """Retorna uma lista de todas as salas ativas."""
        return list(self.active_rooms)

    def room_exists(self, room_id: str) -> bool:
        """Verifica se uma sala existe."""
        return room_id in self.active_rooms

    def remove_room(self, room_id: str):
        """Remove uma sala da lista de ativas se ela existir."""
        if room_id in self.active_rooms:
            self.active_rooms.remove(room_id)
            print(f"Sala {room_id} foi removida.")


room_manager = RoomManager()