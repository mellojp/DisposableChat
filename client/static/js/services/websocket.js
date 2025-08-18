const websocketService = {
    socket: null,
    listeners: {}, // Objeto para armazenar os callbacks (ex: 'chat', 'user_joined')

    /**
     * Inicia a conexão WebSocket com o servidor.
     */
    connect(roomId, username) {
        if (this.socket) {
            this.socket.close();
        }

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/${roomId}/${username}`;
        this.socket = new WebSocket(wsUrl);

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type && this.listeners[data.type]) {
                // Chama o callback registrado para este tipo de evento
                this.listeners[data.type].forEach(callback => callback(data));
            }
        };

        this.socket.onclose = () => {
            if (this.listeners['close']) {
                this.listeners['close'].forEach(callback => callback());
            }
        };

        this.socket.onerror = (error) => {
            console.error("Erro no WebSocket:", error);
            if (this.listeners['error']) {
                this.listeners['error'].forEach(callback => callback(error));
            }
        };
    },

    /**
     * Registra um callback para um tipo de evento específico.
     */
    on(eventName, callback) {
        if (!this.listeners[eventName]) {
            this.listeners[eventName] = [];
        }
        this.listeners[eventName].push(callback);
    },

    /**
     * Envia uma mensagem para o servidor.
     */
    sendMessage(payload) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(payload));
        }
    },

    /**
     * Fecha a conexão.
     */
    close() {
        if (this.socket) {
            this.socket.close();
        }
    }
};