document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENTOS DO DOM ---
    const messagesArea = document.getElementById('messages-area');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const leaveRoomBtn = document.getElementById('leave-room-btn');
    const typingIndicator = document.getElementById('typing-indicator');

    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('visible');
        });
    }
    const chatPanel = document.querySelector('.chat-panel');

    if (chatPanel && sidebar && menuToggle) { // Adicionamos o menuToggle aqui
        chatPanel.addEventListener('click', (event) => {
            // A mágica acontece nesta linha:
            // Verificamos se a sidebar está visível E se o alvo do clique NÃO é o botão de menu
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggle = menuToggle.contains(event.target);

            if (sidebar.classList.contains('visible') && !isClickInsideSidebar && !isClickOnToggle) {
                sidebar.classList.remove('visible');
            }
        });
    }

    const currentUser = sessionStorage.getItem('username');
    const roomId = window.salaId; // Injetado pelo chat.html
    let typingTimer; // Timer para controlar o indicador "is typing"
    const TYPING_TIMER_LENGTH = 2000; // 2 segundos

    if (!currentUser || !roomId) {
        sessionStorage.removeItem('username');
        window.location.href = '/';
        return;
    }

    // --- LÓGICA DO WEBSOCKET ---
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/${roomId}/${currentUser}`;
    const socket = new WebSocket(wsUrl);

    function addMessage(data) {
        const { type, user, message } = data;
        const messageDiv = document.createElement('div');
        
        const isSystemMessage = (type === 'user_joined' || type === 'user_left');
        
        if (isSystemMessage) {
            messageDiv.className = 'message system';
            messageDiv.textContent = message;
        } else if (type === 'chat') {
            // Lógica para diferenciar mensagens enviadas e recebidas
            const messageType = (user === currentUser) ? 'sent' : 'received';
            messageDiv.className = `message ${messageType}`;
            const messagePrefix = (messageType === 'received') ? `${user}: ` : '';
            messageDiv.textContent = `${messagePrefix}${message}`;
        }

        if (messageDiv.className) {
            messagesArea.insertBefore(messageDiv, typingIndicator);
            messagesArea.scrollTop = messagesArea.scrollHeight;
        }
    }

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'typing' && data.user !== currentUser) {
            typingIndicator.textContent = `${data.user} está digitando...`;
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                typingIndicator.textContent = '';
            }, TYPING_TIMER_LENGTH);
            return; // Interrompe para não tratar como uma mensagem de chat
        }

        // Ignora as próprias mensagens de chat (que já são adicionadas localmente)
        if (data.type === 'chat' && data.user === currentUser) {
            return;
        }
        
        // Limpa o indicador de digitação quando uma mensagem real chega
        if (data.user !== currentUser) {
            typingIndicator.textContent = '';
            clearTimeout(typingTimer);
        }

        addMessage(data);
    };

    socket.onclose = () => {
        console.log("Conexão fechada.");
        addMessage({ type: 'user_left', user: 'Sistema', message: 'Você foi desconectado.' });
    };

    socket.onerror = (error) => {
        console.error("Erro no WebSocket:", error);
        addMessage({ type: 'user_left', user: 'Sistema', message: 'Ocorreu um erro de conexão.' });
    };

    messageForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const messageText = messageInput.value.trim();

        if (messageText && socket.readyState === WebSocket.OPEN) {
            const messageData = {
                type: 'chat',
                user: currentUser,
                message: messageText
            };
            addMessage(messageData); // Adiciona a mensagem localmente
            socket.send(JSON.stringify(messageData)); // Envia para o servidor
            messageInput.value = '';
        }
    });

    messageInput.addEventListener('input', () => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'typing', user: currentUser }));
        }
    });

    if (leaveRoomBtn) {
        leaveRoomBtn.addEventListener('click', () => {
            socket.close();
            sessionStorage.removeItem('username');
            window.location.href = '/';
        });
    }
});