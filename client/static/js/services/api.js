const api = {
    /**
     * Faz uma requisição POST para criar uma nova sala.
     */
    async criarNovaSala() {
        const response = await fetch('/rooms', { method: 'POST' });
        if (!response.ok) throw new Error('Falha ao criar a sala.');
        return response.json();
    },

    /**
     * Faz uma requisição GET para verificar se uma sala existe.
     */
    async verificarSeSalaExiste(roomId) {
        const response = await fetch(`/rooms/${roomId}`);
        return response.ok;
    },

    /**
     * Obtém a lista de salas ativas, sincroniza com o sessionStorage e retorna a lista limpa.
     */
    async synchronizeAndGetRooms(currentRoomId) {
        try {
            const response = await fetch('/rooms');
            if (!response.ok) throw new Error('Não foi possível obter a lista de salas ativas.');
            
            const data = await response.json();
            const activeRoomsFromServer = data.rooms || [];
            
            // ALTERADO AQUI: de localStorage para sessionStorage
            let locallySavedRooms = JSON.parse(sessionStorage.getItem('joinedRooms')) || [];

            // Filtra as salas locais, mantendo apenas as que ainda existem no servidor.
            let syncedRooms = locallySavedRooms.filter(room => activeRoomsFromServer.includes(room));

            // Adiciona a sala atual à lista, se ainda não estiver lá.
            if (!syncedRooms.includes(currentRoomId)) {
                syncedRooms.push(currentRoomId);
            }

            // ALTERADO AQUI: de localStorage para sessionStorage
            sessionStorage.setItem('joinedRooms', JSON.stringify(syncedRooms));
            return syncedRooms;

        } catch (error) {
            console.error("Erro ao sincronizar salas:", error);
            // Em caso de erro, trabalha com a lista local para não quebrar a UI.
            
            // ALTERADO AQUI: de localStorage para sessionStorage
            const localRooms = JSON.parse(sessionStorage.getItem('joinedRooms')) || [];
            if (!localRooms.includes(currentRoomId)) {
                localRooms.push(currentRoomId);
            }
            return localRooms;
        }
    }
};