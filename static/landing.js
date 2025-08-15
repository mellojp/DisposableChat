document.addEventListener('DOMContentLoaded', () => {
    const usernameInput = document.getElementById('username-input');
    const roomIdInput = document.getElementById('room-id-input');
    const joinRoomBtn = document.getElementById('join-room-btn');
    const createRoomBtn = document.getElementById('create-room-btn');

    // Função para pegar o nome de usuário e armazenar
    const setUsername = () => {
        const username = usernameInput.value.trim();
        if (!username) {
            alert('Por favor, preencha seu nome ou apelido.');
            return null; // Retorna null se estiver vazio
        }
        sessionStorage.setItem('username', username);
        return username;
    };

    // Evento para o botão CRIAR SALA NOVA
    createRoomBtn.addEventListener('click', async () => {
        const username = setUsername();
        if (!username) {
            return; // Interrompe se o nome de usuário não for válido
        }

        try {
            // Faz a chamada POST para o endpoint que cria a sala
            const response = await fetch('/rooms', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            // Redireciona para a página da sala recém-criada
            window.location.href = `/sala/${data.room_id}`;

        } catch (error) {
            console.error('Falha ao criar a sala:', error);
            alert('Não foi possível conectar ao servidor para criar a sala.');
        }
    });

    // Evento para o botão ENTRAR NA SALA
    joinRoomBtn.addEventListener('click', async () => {
        const roomId = roomIdInput.value.trim();
        const username = setUsername();

        if (!username || !roomId) {
            if (!roomId) alert('Por favor, preencha o código da sala.');
            return;
        }

        try {
            // Verifica se a sala existe fazendo uma chamada GET para a API
            const response = await fetch(`/rooms/${roomId}`);

            if (response.ok) {
                // Se a sala existir, redireciona para a página de chat
                window.location.href = `/sala/${roomId}`;
            } else {
                alert('Erro: Sala não encontrada. Verifique o código e tente novamente.');
            }
        } catch (error) {
            console.error('Falha ao verificar a sala:', error);
            alert('Não foi possível conectar ao servidor.');
        }
    });
});