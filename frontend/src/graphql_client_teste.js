const { GraphQLClient, gql } = require('graphql-request');

// GraphQL endpoint
const endpoint = 'http://localhost:8001/graphql';

// Create GraphQL client
const client = new GraphQLClient(endpoint);

// GraphQL queries and mutations
const queries = {
    listUsers: gql`
        query {
            listUsers {
                id
                nome
                idade
            }
        }
    `,
    listAllMusic: gql`
        query {
            listAllMusic {
                id
                nome
                artista
            }
        }
    `,
    listUserPlaylists: gql`
        query($userId: Int!) {
            listUserPlaylists(userId: $userId) {
                id
                nome
                userId
                musicas {
                    id
                    nome
                    artista
                }
            }
        }
    `,
    listPlaylistMusic: gql`
        query($playlistId: Int!) {
            listPlaylistMusic(playlistId: $playlistId) {
                id
                nome
                artista
            }
        }
    `,
    listPlaylistsByMusic: gql`
        query($musicId: Int!) {
            listPlaylistsByMusic(musicId: $musicId) {
                id
                nome
                userId
                musicas {
                    id
                    nome
                    artista
                }
            }
        }
    `
};

const mutations = {
    addUser: gql`
        mutation($nome: String!, $idade: Int!) {
            addUser(nome: $nome, idade: $idade) {
                id
                nome
                idade
            }
        }
    `,
    addMusic: gql`
        mutation($nome: String!, $artista: String!) {
            addMusic(nome: $nome, artista: $artista) {
                id
                nome
                artista
            }
        }
    `,
    createPlaylist: gql`
        mutation($nome: String!, $userId: Int!) {
            createPlaylist(nome: $nome, userId: $userId) {
                id
                nome
                userId
            }
        }
    `,
    addMusicToPlaylist: gql`
        mutation($playlistId: Int!, $musicId: Int!) {
            addMusicToPlaylist(playlistId: $playlistId, musicId: $musicId) {
                id
                nome
                userId
                musicas {
                    id
                    nome
                    artista
                }
            }
        }
    `
};

async function executarTestes() {
    try {
        console.log('🚀 Iniciando testes do cliente GraphQL...');

        // --- Testando Operações de Adição (CREATE) ---
        console.log("\n--- Adicionando Dados Iniciais ---");

        // Adicionar usuários
        console.log("\nAdicionando usuários...");
        const alice = await client.request(mutations.addUser, {
            nome: "Alice Silva",
            idade: 25
        });
        console.log("Usuário adicionado:", alice.addUser);

        const bruno = await client.request(mutations.addUser, {
            nome: "Bruno Costa",
            idade: 30
        });
        console.log("Usuário adicionado:", bruno.addUser);

        const carla = await client.request(mutations.addUser, {
            nome: "Carla Souza",
            idade: 22
        });
        console.log("Usuário adicionado:", carla.addUser);

        // Adicionar músicas
        console.log("\nAdicionando músicas...");
        const musica1 = await client.request(mutations.addMusic, {
            nome: "O Ritmo da Vida",
            artista: "Banda Sonhos"
        });
        console.log("Música adicionada:", musica1.addMusic);

        const musica2 = await client.request(mutations.addMusic, {
            nome: "Caminho do Sol",
            artista: "Solo Perfeito"
        });
        console.log("Música adicionada:", musica2.addMusic);

        const musica3 = await client.request(mutations.addMusic, {
            nome: "Noite Estrelada",
            artista: "Cantor Desconhecido"
        });
        console.log("Música adicionada:", musica3.addMusic);

        const musica4 = await client.request(mutations.addMusic, {
            nome: "Melodia Secreta",
            artista: "Melodious Band"
        });
        console.log("Música adicionada:", musica4.addMusic);

        // Criar playlists
        console.log("\nCriando playlists...");
        const playlist1 = await client.request(mutations.createPlaylist, {
            nome: "Favoritas da Alice",
            userId: 1
        });
        console.log("Playlist criada:", playlist1.createPlaylist);

        const playlist2 = await client.request(mutations.createPlaylist, {
            nome: "Hits de Rock do Bruno",
            userId: 2
        });
        console.log("Playlist criada:", playlist2.createPlaylist);

        const playlist3 = await client.request(mutations.createPlaylist, {
            nome: "Minhas Mais Novas",
            userId: 1
        });
        console.log("Playlist criada:", playlist3.createPlaylist);

        // Adicionar músicas às playlists
        console.log("\nAdicionando músicas às playlists...");
        const addMusic1 = await client.request(mutations.addMusicToPlaylist, {
            playlistId: 1,
            musicId: 1
        });
        console.log("Música adicionada à playlist:", addMusic1.addMusicToPlaylist);

        const addMusic2 = await client.request(mutations.addMusicToPlaylist, {
            playlistId: 1,
            musicId: 2
        });
        console.log("Música adicionada à playlist:", addMusic2.addMusicToPlaylist);

        const addMusic3 = await client.request(mutations.addMusicToPlaylist, {
            playlistId: 2,
            musicId: 3
        });
        console.log("Música adicionada à playlist:", addMusic3.addMusicToPlaylist);

        const addMusic4 = await client.request(mutations.addMusicToPlaylist, {
            playlistId: 3,
            musicId: 1
        });
        console.log("Música adicionada à playlist:", addMusic4.addMusicToPlaylist);

        const addMusic5 = await client.request(mutations.addMusicToPlaylist, {
            playlistId: 3,
            musicId: 4
        });
        console.log("Música adicionada à playlist:", addMusic5.addMusicToPlaylist);

        // --- Testando Cenários de Erro ---
        console.log("\n--- Testando Cenários de Erro ---");

        // Teste 1: Usuário não existe
        try {
            await client.request(mutations.createPlaylist, {
                nome: "Playlist Inexistente",
                userId: 99
            });
        } catch (error) {
            console.log("Teste 1 (usuário não existe):", error.message);
        }

        // Teste 2: Música já na playlist
        try {
            await client.request(mutations.addMusicToPlaylist, {
                playlistId: 1,
                musicId: 1
            });
        } catch (error) {
            console.log("Teste 2 (música já na playlist):", error.message);
        }

        // Teste 3: Playlist não existe
        try {
            await client.request(mutations.addMusicToPlaylist, {
                playlistId: 99,
                musicId: 1
            });
        } catch (error) {
            console.log("Teste 3 (playlist não existe):", error.message);
        }

        // Teste 4: Música não existe
        try {
            await client.request(mutations.addMusicToPlaylist, {
                playlistId: 1,
                musicId: 99
            });
        } catch (error) {
            console.log("Teste 4 (música não existe):", error.message);
        }

        // --- Testando Operações de Consulta (READ) ---
        console.log("\n--- Testando Operações de Consulta (READ) ---");

        // 1. Listar todos os usuários
        console.log("\n-- Listando todos os usuários --");
        const usuarios = await client.request(queries.listUsers);
        console.log("Usuários:", usuarios.listUsers);

        // 2. Listar todas as músicas
        console.log("\n-- Listando todas as músicas --");
        const musicas = await client.request(queries.listAllMusic);
        console.log("Músicas:", musicas.listAllMusic);

        // 3. Listar playlists de um usuário
        console.log("\n-- Listando playlists do Usuário ID 1 (Alice) --");
        const playlistsUsuario1 = await client.request(queries.listUserPlaylists, { userId: 1 });
        console.log("Playlists do usuário 1:", playlistsUsuario1.listUserPlaylists);

        console.log("\n-- Listando playlists do Usuário ID 99 (inexistente) --");
        const playlistsUsuario99 = await client.request(queries.listUserPlaylists, { userId: 99 });
        console.log("Playlists do usuário 99:", playlistsUsuario99.listUserPlaylists);

        // 4. Listar músicas de uma playlist
        console.log("\n-- Listando músicas da Playlist ID 1 ('Favoritas da Alice') --");
        const musicasNaPl1 = await client.request(queries.listPlaylistMusic, { playlistId: 1 });
        console.log("Músicas na playlist 1:", musicasNaPl1.listPlaylistMusic);

        console.log("\n-- Listando músicas da Playlist ID 99 (inexistente) --");
        const musicasNaPl99 = await client.request(queries.listPlaylistMusic, { playlistId: 99 });
        console.log("Músicas na playlist 99:", musicasNaPl99.listPlaylistMusic);

        // 5. Listar playlists que contêm uma música
        console.log("\n-- Listando playlists que contêm a Música ID 1 ('O Ritmo da Vida') --");
        const playlistsComMusica1 = await client.request(queries.listPlaylistsByMusic, { musicId: 1 });
        console.log("Playlists com música 1:", playlistsComMusica1.listPlaylistsByMusic);

        console.log("\n-- Listando playlists que contêm a Música ID 99 (inexistente) --");
        const playlistsComMusica99 = await client.request(queries.listPlaylistsByMusic, { musicId: 99 });
        console.log("Playlists com música 99:", playlistsComMusica99.listPlaylistsByMusic);

    } catch (erro) {
        console.error("❌ Ocorreu um erro:", erro.message);
        console.log("Certifique-se de que o servidor GraphQL esteja rodando e acessível na porta 8001.");
    }
}

// Executar os testes
executarTestes(); 