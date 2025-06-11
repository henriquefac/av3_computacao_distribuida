const soap = require('strong-soap').soap;

// URL do WSDL do servidor SOAP
const wsdlUrl = 'http://localhost:8000/?wsdl';

async function executarTestes() {
    try {
        console.log('Tentando conectar ao servidor SOAP em:', wsdlUrl);
        
        // Criar cliente SOAP
        const options = {
            endpoint: 'http://localhost:8000',
            forceSoap12Headers: true
        };

        const cliente = await new Promise((resolve, reject) => {
            soap.createClient(wsdlUrl, options, (err, client) => {
                if (err) {
                    reject(err);
                    return;
                }
                resolve(client);
            });
        });

        console.log('Cliente SOAP criado com sucesso!');

        console.log("✨ Operações disponíveis no serviço:");
        console.log(Object.keys(cliente.describe()));

        // --- Testando Operações de Adição (CREATE) ---
        console.log("\n--- Adicionando Dados Iniciais (Executar apenas uma vez para popular o BD) ---");
        
        // Adicionar usuários
        console.log(await new Promise((resolve, reject) => {
            cliente.add_user({ nome: "Alice Silva", idade: 25 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar usuários
        console.log(await new Promise((resolve, reject) => {
            cliente.add_user({ nome: "Bruno Costa", idade: 30 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar usuários
        console.log(await new Promise((resolve, reject) => {
            cliente.add_user({ nome: "Carla Souza", idade: 22 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music({ nome: "O Ritmo da Vida", artista: "Banda Sonhos" }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music({ nome: "Caminho do Sol", artista: "Solo Perfeito" }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music({ nome: "Noite Estrelada", artista: "Cantor Desconhecido" }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music({ nome: "Melodia Secreta", artista: "Melodious Band" }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Criar playlists
        console.log(await new Promise((resolve, reject) => {
            cliente.create_playlist({ nome: "Favoritas da Alice", user_id: 1 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Criar playlists
        console.log(await new Promise((resolve, reject) => {
            cliente.create_playlist({ nome: "Hits de Rock do Bruno", user_id: 2 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Criar playlists
        console.log(await new Promise((resolve, reject) => {
            cliente.create_playlist({ nome: "Minhas Mais Novas", user_id: 1 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas às playlists
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music_to_playlist({ playlist_id: 1, music_id: 1 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas às playlists
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music_to_playlist({ playlist_id: 1, music_id: 2 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas às playlists
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music_to_playlist({ playlist_id: 2, music_id: 3 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas às playlists
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music_to_playlist({ playlist_id: 3, music_id: 1 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // Adicionar músicas às playlists
        console.log(await new Promise((resolve, reject) => {
            cliente.add_music_to_playlist({ playlist_id: 3, music_id: 4 }, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        }));

        // --- Testando Cenários de Erro (adição) ---
        console.log("\n--- Testando Cenários de Erro de Adição ---");
        
        // Teste 1: Usuário não existe
        try {
            await new Promise((resolve, reject) => {
                cliente.create_playlist({ nome: "Playlist Inexistente", user_id: 99 }, (err, result) => {
                    if (err) resolve(err);
                    else resolve(result);
                });
            });
        } catch (error) {
            console.log("  Teste 1 (usuário não existe):", error.message);
        }

        // Teste 2: Música já na playlist
        try {
            await new Promise((resolve, reject) => {
                cliente.add_music_to_playlist({ playlist_id: 1, music_id: 1 }, (err, result) => {
                    if (err) resolve(err);
                    else resolve(result);
                });
            });
        } catch (error) {
            console.log("  Teste 2 (música já na playlist):", error.message);
        }

        // Teste 3: Playlist não existe
        try {
            await new Promise((resolve, reject) => {
                cliente.add_music_to_playlist({ playlist_id: 99, music_id: 1 }, (err, result) => {
                    if (err) resolve(err);
                    else resolve(result);
                });
            });
        } catch (error) {
            console.log("  Teste 3 (playlist não existe):", error.message);
        }

        // Teste 4: Música não existe
        try {
            await new Promise((resolve, reject) => {
                cliente.add_music_to_playlist({ playlist_id: 1, music_id: 99 }, (err, result) => {
                    if (err) resolve(err);
                    else resolve(result);
                });
            });
        } catch (error) {
            console.log("  Teste 4 (música não existe):", error.message);
        }

        // --- Testando Operações de Consulta (READ) ---
        console.log("\n--- Testando Operações de Consulta (READ) ---");

        // 1. Listar todos os usuários
console.log("\n-- Listando todos os usuários --");
try {
    const usuarios = await new Promise((resolve, reject) => {
        cliente.list_users((err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });

    const usuariosList = usuarios?.list_usersResult;
    if (usuariosList) {
        const lista = Array.isArray(usuariosList) ? usuariosList : [usuariosList];
        if (lista.length > 0) {
            lista.forEach(usuario => {
                console.log(`  ID do Usuário: ${usuario.id}, Nome: ${usuario.nome}, Idade: ${usuario.idade}`);
            });
        } else {
            console.log("  Nenhum usuário encontrado.");
        }
    } else {
        console.log("  Nenhum dado retornado.");
    }
} catch (error) {
    console.log("  Erro ao listar usuários:", error.message);
}

console.log("\n-- Listando todas as músicas --");
try {
    const musicas = await new Promise((resolve, reject) => {
        cliente.list_all_music((err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });

    const musicasList = musicas?.list_all_musicResult;
    if (musicasList) {
        const lista = Array.isArray(musicasList) ? musicasList : [musicasList];
        if (lista.length > 0) {
            lista.forEach(musica => {
                console.log(`  ID da Música: ${musica.id}, Nome: ${musica.nome}, Artista: ${musica.artista}`);
            });
        } else {
            console.log("  Nenhuma música encontrada.");
        }
    } else {
        console.log("  Nenhum dado retornado.");
    }
} catch (error) {
    console.log("  Erro ao listar músicas:", error.message);
}

        // 3. Listar playlists de um usuário (ex: user_id=1)
console.log("\n-- Listando playlists do Usuário ID 1 (Alice) --");
try {
    const playlists = await new Promise((resolve, reject) => {
        cliente.list_user_playlists({ user_id: 1 }, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });

    const playlistsList = playlists?.list_user_playlistsResult;
    if (playlistsList) {
        const lista = Array.isArray(playlistsList) ? playlistsList : [playlistsList];
        if (lista.length > 0) {
            lista.forEach(playlist => {
                console.log(`  ID da Playlist: ${playlist.id}, Nome: ${playlist.nome}, ID do Usuário: ${playlist.user_id}`);
            });
        } else {
            console.log("  Nenhuma playlist encontrada para o usuário ID 1.");
        }
    } else {
        console.log("  Nenhum dado retornado.");
    }
} catch (error) {
    console.log("  Erro ao listar playlists do usuário 1:", error.message);
}

console.log("\n-- Listando playlists do Usuário ID 99 (inexistente) --");
try {
    const playlistsUsuario99 = await new Promise((resolve, reject) => {
        cliente.list_user_playlists({ user_id: 99 }, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });

    if (playlistsUsuario99) {
        const list_playlistsUsuario99 = playlistsUsuario99["list_user_playlistsResult"];

        if (Array.isArray(list_playlistsUsuario99) && list_playlistsUsuario99.length > 0) {
            list_playlistsUsuario99.forEach(pl => {
                console.log(`  ID da Playlist: ${pl.id}, Nome: ${pl.nome}, ID do Usuário: ${pl.user_id}`);
            });
        } else {
            console.log("  Nenhuma playlist encontrada para o usuário ID 99 (esperado, lista vazia).");
        }
    } else {
        console.log("  Sem resposta");
    }
} catch (error) {
    console.log("  Erro ao listar playlists do usuário 99:", error.message);
}

        // 4. Listar músicas de uma playlist (ex: playlist_id=1)
console.log("\n-- Listando músicas da Playlist ID 1 ('Favoritas da Alice') --");
try {
    const musicasNaPl1 = await new Promise((resolve, reject) => {
        cliente.list_playlist_music({ playlist_id: 1 }, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });

    if (musicasNaPl1) {
        const list_musicasNaPl1 = musicasNaPl1["list_playlist_musicResult"];
        
        if (Array.isArray(list_musicasNaPl1) && list_musicasNaPl1.length > 0) {
            list_musicasNaPl1.forEach(musica => {
                console.log(`  Música na Playlist ID 1: '${musica.nome}' por '${musica.artista}' (ID: ${musica.id})`);
            });
        } else {
            console.log("  Nenhuma música encontrada na playlist ID 1.");
        }
    } else {
        console.log("  Sem resposta");
    }
} catch (error) {
    console.log("  Erro ao listar músicas da playlist 1:", error.message);
}
console.log("\n-- Listando músicas da Playlist ID 99 (inexistente) --");
try {
    const musicasNaPl99 = await new Promise((resolve, reject) => {
        cliente.list_playlist_music({ playlist_id: 99 }, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });

    if (musicasNaPl99) {
        const list_musicasNaPl99 = musicasNaPl99["list_playlist_musicResult"];

        if (Array.isArray(list_musicasNaPl99) && list_musicasNaPl99.length > 0) {
            list_musicasNaPl99.forEach(musica => {
                console.log(`  Música na Playlist ID 99: '${musica.nome}' por '${musica.artista}' (ID: ${musica.id})`);
            });
        } else {
            console.log("  Nenhuma música encontrada na playlist ID 99 (esperado, lista vazia).");
        }
    } else {
        console.log("  Sem resposta");
    }
} catch (error) {
    console.log("  Erro ao listar músicas da playlist 99:", error.message);
}

// 5. Listar playlists que contêm uma música (ex: music_id=1)
console.log("\n-- Listando playlists que contêm a Música ID 1 ('O Ritmo da Vida') --");
try {
    const playlistsComMusica1 = await new Promise((resolve, reject) => {
        cliente.list_playlists_by_music({ music_id: 1 }, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });

    if (playlistsComMusica1) {
        const list_playlistsComMusica1 = playlistsComMusica1["list_playlists_by_musicResult"];

        if (Array.isArray(list_playlistsComMusica1) && list_playlistsComMusica1.length > 0) {
            list_playlistsComMusica1.forEach(pl => {
                console.log(`  Playlist com Música ID 1: ID ${pl.id}, Nome: '${pl.nome}' (ID do Usuário: ${pl.user_id})`);
            });
        } else {
            console.log("  Nenhuma playlist encontrada contendo a música ID 1.");
        }
    } else {
        console.log("  Sem resposta");
    }
} catch (error) {
    console.log("  Erro ao listar playlists com música 1:", error.message);
}
console.log("\n-- Listando playlists que contêm a Música ID 99 (inexistente) --");
try {
    const playlistsComMusica99 = await new Promise((resolve, reject) => {
        cliente.list_playlists_by_music({ music_id: 99 }, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });

    if (playlistsComMusica99) {
        const list_playlistsComMusica99 = playlistsComMusica99["list_playlists_by_musicResult"];

        if (Array.isArray(list_playlistsComMusica99) && list_playlistsComMusica99.length > 0) {
            list_playlistsComMusica99.forEach(pl => {
                console.log(`  Playlist com Música ID 99: ID ${pl.id}, Nome: '${pl.nome}' (ID do Usuário: ${pl.user_id})`);
            });
        } else {
            console.log("  Nenhuma playlist encontrada contendo a música ID 99 (esperado, lista vazia).");    
        }
    } else {
        console.log("  Sem resposta");
    }
} catch (error) {
    console.log("  Erro ao listar playlists com música 99:", error.message);
}

    } catch (erro) {
        console.error("❌ Ocorreu um erro:", erro.message);
        console.log("Certifique-se de que o servidor SOAP esteja rodando e acessível na porta 8000.");
    }
}

// Executar os testes
executarTestes();