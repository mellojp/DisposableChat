document.addEventListener('DOMContentLoaded', () => {

    // --- ELEMENTOS DO DOM ---
    const messagesArea = document.getElementById('messages-area');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const leaveRoomBtn = document.getElementById('leave-room-btn'); // Botão de sair

    // --- ESTADO DO CLIENTE ---
    const currentUser = sessionStorage.getItem('username') || "Anônimo";

    // --- LÓGICA PARA SAIR DA SALA ---
    if (leaveRoomBtn) {
        leaveRoomBtn.addEventListener('click', () => {
            // Fecha a conexão do WebSocket se estiver aberta
            if (window.chatSocket && window.chatSocket.readyState === WebSocket.OPEN) {
                window.chatSocket.close();
            }
            // Limpa o nome de usuário armazenado
            sessionStorage.removeItem('username');
            // Redireciona o usuário para a página inicial
            window.location.href = '/';
        });
    }

    // Evita criar múltiplas conexões se a página disparar DOMContentLoaded mais de uma vez
    if (!window.chatSocket || window.chatSocket.readyState === WebSocket.CLOSED) {
        const wsUrl = `ws://${window.location.host}/ws/${window.salaId}`;
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
            messageDiv.classList.add('system'); // Classe extra para sistema
        }

        const messagePrefix = (messageType === 'received' && !isSystemMessage) ? `${user}: ` : '';
        messageDiv.textContent = `${messagePrefix}${message}`;

        messagesArea.appendChild(messageDiv);
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    // --- GERENCIAMENTO DA CONEXÃO WEBSOCKET ---
    socket.onopen = () => {
        console.log("Conexão estabelecida!");
        socket.send(JSON.stringify({ user: currentUser, message: "" }));
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.user === currentUser && data.message) {
            return;
        }
        addMessage(data);
    };

    socket.onclose = () => {
        console.log("Conexão fechada.");
        // Apenas adiciona a mensagem se o usuário ainda estiver na página de chat.
        if (document.getElementById('messages-area')) {
             addMessage({ user: 'Sistema', message: 'Você foi desconectado. Por favor volte ao início.' });
        }
    };

    socket.onerror = (error) => {
        console.error("Erro no WebSocket:", error);
        addMessage({ user: 'Sistema', message: 'Ocorreu um erro de conexão.' });
    };

    // --- ENVIO DE MENSAGENS ---
    messageForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const messageText = messageInput.value.trim();

        if (messageText && socket.readyState === WebSocket.OPEN) {
            addMessage({ user: currentUser, message: messageText });
            socket.send(JSON.stringify({
                user: currentUser,
                message: messageText
            }));
            messageInput.value = '';
        }
    });
});