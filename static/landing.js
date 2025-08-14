document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username-input');
    const roomIdInput = document.getElementById('room-id-input');
    const joinRoomBtn = document.getElementById('join-room-btn');
    const createRoomBtn = document.getElementById('create-room-btn');

    // Função para pegar o nome de usuário e armazenar
    const setUsername = () => {
        const username = usernameInput.value.trim();
        if (!username) {
            alert('Por favor, preencha seu nome de usuário.');
            return false;
        }
        sessionStorage.setItem('username', username);
        return true;
    };

    // Evento para o botão ENTRAR NA SALA
    joinRoomBtn.addEventListener('click', async () => {
        const roomId = roomIdInput.value.trim();

        if (!setUsername()) {
            return;
        }
        
        if (!roomId) {
            alert('Por favor, preencha o código da sala.');
            return;
        }

        try {
            // Verifica se a sala existe antes de redirecionar
            const response = await fetch(`/sala/join/${roomId}`, {
                method: 'POST'
            });

            if (response.ok) {
                window.location.href = `/sala/${roomId}`;
            } else {
                alert('Erro: Sala não encontrada. Verifique o código e tente novamente.');
            }
        } catch (error) {
            console.error('Falha ao verificar a sala:', error);
            alert('Não foi possível conectar ao servidor. Tente novamente mais tarde.');
        }
    });

    // Evento para o botão CRIAR SALA NOVA
    createRoomBtn.addEventListener('click', () => {
        if (setUsername()) {
            window.location.href = `/sala/create`;
        }
    });
});