const messageStore = {
    /**
     * Adiciona uma nova mensagem ao histórico de uma sala específica.
     * @param {string} roomId - O ID da sala.
     * @param {object} messageData - O objeto da mensagem a ser guardado.
     */
    addMessage(roomId, messageData) {
        const allHistories = this._getAllHistories();
        if (!allHistories[roomId]) {
            allHistories[roomId] = [];
        }
        allHistories[roomId].push(messageData);
        sessionStorage.setItem('chatHistories', JSON.stringify(allHistories));
    },

    /**
     * Obtém o histórico de mensagens para uma sala específica.
     * @param {string} roomId - O ID da sala.
     * @returns {Array} - Uma lista de objetos de mensagem.
     */
    getMessages(roomId) {
        const allHistories = this._getAllHistories();
        return allHistories[roomId] || [];
    },

    /**
     * Função auxiliar para obter todos os históricos do sessionStorage.
     * @private
     */
    _getAllHistories() {
        try {
            return JSON.parse(sessionStorage.getItem('chatHistories')) || {};
        } catch (e) {
            return {};
        }
    }
};