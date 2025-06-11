const axios = require('axios');

// REST API endpoint
const API_URL = 'http://localhost:8000';

async function executarTestes() {
    try {
        console.log('🚀 Iniciando testes do cliente REST...');

        // --- Testando Operações de Adição (CREATE) ---
        console.log("\n--- Adicionando Dados Iniciais ---");

        // Adicionar usuários
        console.log("\nAdicionando usuários...");
        const alice = await axios.post(`${API_URL}/users/`, {
            nome: "Alice Silva",
            idade: 25
        });
        console.log("Usuário adicionado:", alice.data);

        const bruno = await axios.post(`${API_URL}/users/`, {
            nome: "Bruno Costa",
            idade: 30
        });
        console.log("Usuário adicionado:", bruno.data);

        const carla = await axios.post(`${API_URL}/users/`, {
            nome: "Carla Souza",
            idade: 22
        });
        console.log("Usuário adicionado:", carla.data);

        // Adicionar músicas
        console.log("\nAdicionando músicas...");
        const musica1 = await axios.post(`${API_URL}/music/`, {
            nome: "O Ritmo da Vida",
            artista: "Banda Sonhos"
        });
        console.log("Música adicionada:", musica1.data);

        const musica2 = await axios.post(`${API_URL}/music/`, {
            nome: "Caminho do Sol",
            artista: "Solo Perfeito"
        });
        console.log("Música adicionada:", musica2.data);

        const musica3 = await axios.post(`${API_URL}/music/`, {
            nome: "Noite Estrelada",
            artista: "Cantor Desconhecido"
        });
        console.log("Música adicionada:", musica3.data);

        const musica4 = await axios.post(`${API_URL}/music/`, {
            nome: "Melodia Secreta",
            artista: "Melodious Band"
        });
        console.log("Música adicionada:", musica4.data);

        // Criar playlists
        console.log("\nCriando playlists...");
        const playlist1 = await axios.post(`${API_URL}/playlists/`, {
            nome: "Favoritas da Alice",
            user_id: 1
        });
        console.log("Playlist criada:", playlist1.data);

        const playlist2 = await axios.post(`${API_URL}/playlists/`, {
            nome: "Hits de Rock do Bruno",
            user_id: 2
        });
        console.log("Playlist criada:", playlist2.data);

        const playlist3 = await axios.post(`${API_URL}/playlists/`, {
            nome: "Minhas Mais Novas",
            user_id: 1
        });
        console.log("Playlist criada:", playlist3.data);

        // Adicionar músicas às playlists
        console.log("\nAdicionando músicas às playlists...");
        const addMusic1 = await axios.post(`${API_URL}/playlists/1/music/`, {
            music_id: 1
        });
        console.log("Música adicionada à playlist:", addMusic1.data);

        const addMusic2 = await axios.post(`${API_URL}/playlists/1/music/`, {
            music_id: 2
        });
        console.log("Música adicionada à playlist:", addMusic2.data);

        const addMusic3 = await axios.post(`${API_URL}/playlists/2/music/`, {
            music_id: 3
        });
        console.log("Música adicionada à playlist:", addMusic3.data);

        const addMusic4 = await axios.post(`${API_URL}/playlists/3/music/`, {
            music_id: 1
        });
        console.log("Música adicionada à playlist:", addMusic4.data);

        const addMusic5 = await axios.post(`${API_URL}/playlists/3/music/`, {
            music_id: 4
        });
        console.log("Música adicionada à playlist:", addMusic5.data);

        // --- Testando Cenários de Erro ---
        console.log("\n--- Testando Cenários de Erro ---");

        // Teste 1: Usuário não existe
        try {
            await axios.post(`${API_URL}/playlists/`, {
                nome: "Playlist Inexistente",
                user_id: 99
            });
        } catch (error) {
            console.log("Teste 1 (usuário não existe):", error.response?.data?.detail || error.message);
        }

        // Teste 2: Música já na playlist
        try {
            await axios.post(`${API_URL}/playlists/1/music/`, {
                music_id: 1
            });
        } catch (error) {
            console.log("Teste 2 (música já na playlist):", error.response?.data?.detail || error.message);
        }

        // Teste 3: Playlist não existe
        try {
            await axios.post(`${API_URL}/playlists/99/music/`, {
                music_id: 1
            });
        } catch (error) {
            console.log("Teste 3 (playlist não existe):", error.response?.data?.detail || error.message);
        }

        // Teste 4: Música não existe
        try {
            await axios.post(`${API_URL}/playlists/1/music/`, {
                music_id: 99
            });
        } catch (error) {
            console.log("Teste 4 (música não existe):", error.response?.data?.detail || error.message);
        }

        // --- Testando Operações de Consulta (READ) ---
        console.log("\n--- Testando Operações de Consulta (READ) ---");

        // 1. Listar todos os usuários
        console.log("\n-- Listando todos os usuários --");
        const usuarios = await axios.get(`${API_URL}/users/`);
        console.log("Usuários:", usuarios.data);

        // 2. Listar todas as músicas
        console.log("\n-- Listando todas as músicas --");
        const musicas = await axios.get(`${API_URL}/music/`);
        console.log("Músicas:", musicas.data);

        // 3. Listar playlists de um usuário
        console.log("\n-- Listando playlists do Usuário ID 1 (Alice) --");
        const playlistsUsuario1 = await axios.get(`${API_URL}/users/1/playlists/`);
        console.log("Playlists do usuário 1:", playlistsUsuario1.data);

        console.log("\n-- Listando playlists do Usuário ID 99 (inexistente) --");
        try {
            const playlistsUsuario99 = await axios.get(`${API_URL}/users/99/playlists/`);
            console.log("Playlists do usuário 99:", playlistsUsuario99.data);
        } catch (error) {
            console.log("Erro ao listar playlists do usuário 99:", error.response?.data?.detail || error.message);
        }

        // 4. Listar músicas de uma playlist
        console.log("\n-- Listando músicas da Playlist ID 1 ('Favoritas da Alice') --");
        const musicasNaPl1 = await axios.get(`${API_URL}/playlists/1/music/`);
        console.log("Músicas na playlist 1:", musicasNaPl1.data);

        console.log("\n-- Listando músicas da Playlist ID 99 (inexistente) --");
        try {
            const musicasNaPl99 = await axios.get(`${API_URL}/playlists/99/music/`);
            console.log("Músicas na playlist 99:", musicasNaPl99.data);
        } catch (error) {
            console.log("Erro ao listar músicas da playlist 99:", error.response?.data?.detail || error.message);
        }

        // 5. Listar playlists que contêm uma música
        console.log("\n-- Listando playlists que contêm a Música ID 1 ('O Ritmo da Vida') --");
        const playlistsComMusica1 = await axios.get(`${API_URL}/music/1/playlists/`);
        console.log("Playlists com música 1:", playlistsComMusica1.data);

        console.log("\n-- Listando playlists que contêm a Música ID 99 (inexistente) --");
        try {
            const playlistsComMusica99 = await axios.get(`${API_URL}/music/99/playlists/`);
            console.log("Playlists com música 99:", playlistsComMusica99.data);
        } catch (error) {
            console.log("Erro ao listar playlists com música 99:", error.response?.data?.detail || error.message);
        }

    } catch (erro) {
        console.error("❌ Ocorreu um erro:", erro.message);
        console.log("Certifique-se de que o servidor REST esteja rodando e acessível na porta 8000.");
    }
}

// Executar os testes
executarTestes(); 