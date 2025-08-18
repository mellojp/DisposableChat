// /client/static/js/views/chat.js
document.addEventListener('DOMContentLoaded', async () => {
    // --- ELEMENTOS DO DOM (UI) ---
    const messagesArea = document.getElementById('messages-area');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const leaveRoomBtn = document.getElementById('leave-room-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const roomListElement = document.querySelector('.room-list');
    const newRoomIdInput = document.getElementById('new-room-id-input');
    const joinNewRoomBtn = document.getElementById('join-new-room-btn');
    const createNewRoomBtn = document.getElementById('create-new-room-btn');

    // --- ESTADO DA APLICAÇÃO ---
    const currentUser = sessionStorage.getItem('username');
    const roomId = window.salaId;
    let typingTimer;
    let joinedRooms = [];

    // --- FUNÇÕES DE LÓGICA E RENDERIZAÇÃO ---

    function handleLeaveRoom(roomToLeaveId) {
        joinedRooms = joinedRooms.filter(id => id !== roomToLeaveId);
        sessionStorage.setItem('joinedRooms', JSON.stringify(joinedRooms));
        
        let hasJoinedBefore = JSON.parse(sessionStorage.getItem('hasJoinedRooms')) || [];
        hasJoinedBefore = hasJoinedBefore.filter(id => id !== roomToLeaveId);
        sessionStorage.setItem('hasJoinedRooms', JSON.stringify(hasJoinedBefore));

        // Comportamento melhorado ao apagar a sala atual
        if (roomToLeaveId === roomId) {
            // Se houver outras salas, navega para a primeira da lista
            if (joinedRooms.length > 0) {
                window.location.href = `/sala/${joinedRooms[0]}`;
            } else {
                // Se for a última sala, vai para a página inicial
                window.location.href = '/';
            }
        } else {
            // Se apagou outra sala, apenas atualiza a lista na UI
            renderRoomList(joinedRooms, roomId);
        }
    }

    function renderRoomList(rooms, currentRoomId) {
        if (!roomListElement) return;
        roomListElement.innerHTML = '';
        rooms.forEach(id => {
            const item = document.createElement('li');
            item.className = 'room-item';
            if (id === currentRoomId) item.classList.add('active');

            item.innerHTML = `
                <div class="room-icon">#</div>
                <div class="room-details">
                    <h3>Sala</h3>
                    <p>${id}</p>
                </div>
                <button class="delete-room-btn" title="Remover sala da lista">
                    <i class="fa-solid fa-trash"></i>
                </button>
            `;

            // O `div` dos detalhes da sala é agora o alvo do clique para navegação
            const detailsDiv = item.querySelector('.room-details');
            detailsDiv.addEventListener('click', () => {
                if (id !== currentRoomId) {
                    window.location.href = `/sala/${id}`;
                }
            });

            const deleteBtn = item.querySelector('.delete-room-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Essencial para não disparar outros cliques
                handleLeaveRoom(id);
            });

            roomListElement.appendChild(item);
        });
    }

    function addMessage(data, save = true) {
        const { type, user, message } = data;
        const div = document.createElement('div');

        if (type === 'user_joined' || type === 'user_left') {
            div.className = 'message system';
            div.textContent = message;
        } else if (type === 'chat') {
            const messageType = (user === currentUser) ? 'sent' : 'received';
            div.className = `message ${messageType}`;
            const prefix = (messageType === 'received') ? `${user}: ` : '';
            div.textContent = `${prefix}${message}`;
        }

        if (div.className) {
            messagesArea.insertBefore(div, typingIndicator);
            messagesArea.scrollTop = messagesArea.scrollHeight;
        }
        
        if (save && (type === 'chat' || type === 'user_joined' || type === 'user_left')) {
            messageStore.addMessage(roomId, data);
        }
    }

    function loadMessageHistory() {
        const history = messageStore.getMessages(roomId);
        history.forEach(msg => addMessage(msg, false));
    }

    // --- INICIALIZAÇÃO E EVENTOS ---
    if (!currentUser || !roomId) {
        sessionStorage.removeItem('username');
        window.location.href = '/';
        return;
    }

    joinedRooms = await api.synchronizeAndGetRooms(roomId);
    renderRoomList(joinedRooms, roomId);

    loadMessageHistory();

    websocketService.connect(roomId, currentUser);

    websocketService.on('chat', (data) => {
        if (data.user !== currentUser) {
             typingIndicator.textContent = '';
             clearTimeout(typingTimer);
             addMessage(data);
        }
    });

    websocketService.on('user_joined', (data) => {
        if (data.user !== currentUser) {
            addMessage(data);
            return;
        }
        let hasJoinedBefore = JSON.parse(sessionStorage.getItem('hasJoinedRooms')) || [];
        if (!hasJoinedBefore.includes(roomId)) {
            addMessage(data);
            hasJoinedBefore.push(roomId);
            sessionStorage.setItem('hasJoinedRooms', JSON.stringify(hasJoinedBefore));
        }
    });

    websocketService.on('user_left', addMessage);

    websocketService.on('typing', (data) => {
        if (data.user !== currentUser) {
            typingIndicator.textContent = `${data.user} está a digitar...`;
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => { typingIndicator.textContent = ''; }, 2000);
        }
    });

    websocketService.on('close', () => addMessage({ type: 'user_left', user: 'Sistema', message: 'Você foi desconectado.' }));
    websocketService.on('error', () => addMessage({ type: 'user_left', user: 'Sistema', message: 'Ocorreu um erro de conexão.' }));

    messageForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const messageText = messageInput.value.trim();
        if (messageText) {
            const messageData = { type: 'chat', user: currentUser, message: messageText };
            addMessage(messageData);
            websocketService.sendMessage(messageData);
            messageInput.value = '';
        }
    });

    messageInput.addEventListener('input', () => {
        websocketService.sendMessage({ type: 'typing', user: currentUser });
    });

    leaveRoomBtn.addEventListener('click', () => {
        websocketService.close();
        sessionStorage.removeItem('username');
        window.location.href = '/';
    });
    
    joinNewRoomBtn.addEventListener('click', async () => {
        const newRoomId = newRoomIdInput.value.trim();
        if (newRoomId) {
            try {
                if (await api.verificarSeSalaExiste(newRoomId)) {
                    window.location.href = `/sala/${newRoomId}`;
                } else {
                    alert('Erro: Sala não encontrada.');
                }
            } catch (error) {
                console.error(error);
                alert('Não foi possível conectar ao servidor.');
            }
        }
    });

    createNewRoomBtn.addEventListener('click', async () => {
        try {
            const data = await api.criarNovaSala();
            window.location.href = `/sala/${data.room_id}`;
        } catch(error) {
            console.error(error);
            alert('Não foi possível criar a sala.');
        }
    });

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => sidebar.classList.toggle('visible'));
    }
    const chatPanel = document.querySelector('.chat-panel');
    if (chatPanel && sidebar && menuToggle) {
        chatPanel.addEventListener('click', (event) => {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggle = menuToggle.contains(event.target);
            if (sidebar.classList.contains('visible') && !isClickInsideSidebar && !isClickOnToggle) {
                sidebar.classList.remove('visible');
            }
        });
    }
});