document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username-input');
    const roomIdInput = document.getElementById('room-id-input');
    const joinRoomBtn = document.getElementById('join-room-btn');
    const createRoomBtn = document.getElementById('create-room-btn');

    const setUsername = () => {
        const username = usernameInput.value.trim();
        if (!username) {
            alert('Por favor, preencha seu nome ou apelido.');
            return null;
        }
        sessionStorage.setItem('username', username);
        return username;
    };

    createRoomBtn.addEventListener('click', async () => {
        if (!setUsername()) return;
        try {
            const data = await api.criarNovaSala();
            window.location.href = `/sala/${data.room_id}`;
        } catch (error) {
            console.error(error);
            alert('Não foi possível conectar ao servidor para criar a sala.');
        }
    });

    joinRoomBtn.addEventListener('click', async () => {
        const roomId = roomIdInput.value.trim();
        if (!setUsername() || !roomId) {
            if (!roomId) alert('Por favor, preencha o código da sala.');
            return;
        }
        try {
            const salaExiste = await api.verificarSeSalaExiste(roomId);
            if (salaExiste) {
                window.location.href = `/sala/${roomId}`;
            } else {
                alert('Erro: Sala não encontrada. Verifique o código e tente novamente.');
            }
        } catch (error) {
            console.error(error);
            alert('Não foi possível conectar ao servidor.');
        }
    });
});