document.addEventListener('DOMContentLoaded', () => {

    // --- ELEMENTOS DO DOM ---
    const messagesArea = document.getElementById('messages-area');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const leaveRoomBtn = document.getElementById('leave-room-btn');
    const typingIndicator = document.getElementById('typing-indicator'); // Novo elemento

    // --- ESTADO DO CLIENTE ---
    const currentUser = sessionStorage.getItem('username') || "Anônimo";
    if(currentUser == "Anônimo"){
        if (window.chatSocket && window.chatSocket.readyState === WebSocket.OPEN) {
            window.chatSocket.close();
        }
        sessionStorage.removeItem('username');
        window.location.href = '/';
    }
    let typingTimer; // Timer para controlar o indicador
    const TYPING_TIMER_LENGTH = 2000; // 2 segundos

    const sidebar = document.querySelector('.sidebar');
    const menuToggleBtn = document.getElementById('menu-toggle-btn');
    const chatPanel = document.querySelector('.chat-panel');

    if (menuToggleBtn && sidebar) {
        menuToggleBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            sidebar.classList.toggle('visible');
        });

        chatPanel.addEventListener('click', () => {
            if (sidebar.classList.contains('visible')) {
                sidebar.classList.remove('visible');
            }
        });
    }

    if (leaveRoomBtn) {
        leaveRoomBtn.addEventListener('click', () => {
            if (window.chatSocket && window.chatSocket.readyState === WebSocket.OPEN) {
                window.chatSocket.close();
            }
            sessionStorage.removeItem('username');
            window.location.href = '/';
        });
    }

    if (!window.chatSocket || window.chatSocket.readyState === WebSocket.CLOSED) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/${window.salaId}`;
        
        window.chatSocket = new WebSocket(wsUrl);
    }
    const socket = window.chatSocket;

    function addMessage(data) {
        const { user, message } = data;
        const messageDiv = document.createElement('div');
        const messageType = (user === currentUser) ? 'sent' : 'received';
        const isSystemMessage = (user === 'Sistema');

        messageDiv.className = `message ${messageType}`;
        if (isSystemMessage) {
            messageDiv.classList.add('system');
        }

        const messagePrefix = (messageType === 'received' && !isSystemMessage) ? `${user}: ` : '';
        messageDiv.textContent = `${messagePrefix}${message}`;

        // Insere a mensagem antes do indicador de digitação
        messagesArea.insertBefore(messageDiv, typingIndicator);
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    socket.onopen = () => {
        console.log("Conexão estabelecida!");
        socket.send(JSON.stringify({ user: currentUser, message: "" }));
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Novo: Trata o evento de 'typing'
        if (data.type === 'typing' && data.user !== currentUser) {
            typingIndicator.textContent = `${data.user} está digitando...`;
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                typingIndicator.textContent = '';
            }, TYPING_TIMER_LENGTH);
            return;
        }

        if (data.user === currentUser && data.message) {
            return;
        }
        
        // Limpa o indicador quando uma mensagem chega
        if (data.user !== currentUser) {
            typingIndicator.textContent = '';
            clearTimeout(typingTimer);
        }
        addMessage(data);
    };

    socket.onclose = () => {
        console.log("Conexão fechada.");
        if (document.getElementById('messages-area')) {
             addMessage({ user: 'Sistema', message: 'Você foi desconectado. Por favor volte ao início.' });
        }
    };

    socket.onerror = (error) => {
        console.error("Erro no WebSocket:", error);
        addMessage({ user: 'Sistema', message: 'Ocorreu um erro de conexão.' });
    };

    messageForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const messageText = messageInput.value.trim();

        if (messageText && socket.readyState === WebSocket.OPEN) {
            const messageData = {
                type: 'chat', // Define o tipo como 'chat'
                user: currentUser,
                message: messageText
            };
            addMessage(messageData); // Adiciona a mensagem localmente
            socket.send(JSON.stringify(messageData)); // Envia para o servidor
            messageInput.value = '';
        }
    });

    // Novo: Event listener para o campo de input
    messageInput.addEventListener('input', () => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'typing', user: currentUser }));
        }
    });
});