# meu_cliente_soap_bd.py

from zeep import Client
from zeep.exceptions import Fault

# A URL do WSDL do seu servidor SOAP local
# Certifique-se de que o servidor esteja rodando na porta 8000
wsdl_url = 'http://127.0.0.1:8000/?wsdl'

try:
    # 1. Cria uma instância do cliente Zeep.
    # O Zeep lê o WSDL e 'descobre' as operações e tipos do serviço automaticamente.
    client = Client(wsdl=wsdl_url)

    print("✨ Operações disponíveis no serviço (Zeep):")
    # Imprime os métodos que o Zeep descobriu para uma visão clara da interface.
    # A linha 'for service in client.wsdl.services.values(): print(service.name)'
    # imprime apenas os nomes dos serviços. Para ver as operações de um serviço, use client.service.
    print(client.service) # Isso já lista todas as operações de forma legível.

    # --- Testando as operações de Adição (CREATE) ---
    # Rode esta seção apenas uma vez para popular o banco de dados.
    # Se você reiniciar o servidor e o banco de dados for recriado, pode rodar novamente.
    print("\n--- Adicionando Dados Iniciais (Rodar apenas uma vez para popular o DB) ---")
    print(client.service.add_user(nome="Alice Silva", idade=25)) # ID 1
    print(client.service.add_user(nome="Bruno Costa", idade=30)) # ID 2
    print(client.service.add_user(nome="Carla Souza", idade=22)) # ID 3

    print(client.service.add_music(nome="O Ritmo da Vida", artista="Banda Sonhos")) # ID 1
    print(client.service.add_music(nome="Caminho do Sol", artista="Solo Perfeito")) # ID 2
    print(client.service.add_music(nome="Noite Estrelada", artista="Cantor Desconhecido")) # ID 3
    print(client.service.add_music(nome="Melodia Secreta", artista="Melodious Band")) # ID 4

    print(client.service.create_playlist(nome="Favoritas da Alice", user_id=1)) # ID 1
    print(client.service.create_playlist(nome="Hits de Rock do Bruno", user_id=2)) # ID 2
    print(client.service.create_playlist(nome="Minhas Mais Novas", user_id=1)) # ID 3

    print(client.service.add_music_to_playlist(playlist_id=1, music_id=1)) # Playlist 1 tem Música 1
    print(client.service.add_music_to_playlist(playlist_id=1, music_id=2)) # Playlist 1 tem Música 2
    print(client.service.add_music_to_playlist(playlist_id=2, music_id=3)) # Playlist 2 tem Música 3
    print(client.service.add_music_to_playlist(playlist_id=3, music_id=1)) # Playlist 3 tem Música 1
    print(client.service.add_music_to_playlist(playlist_id=3, music_id=4)) # Playlist 3 tem Música 4

    # --- Testando os Cenários de Erro (adição) ---
    print("\n--- Testando Cenários de Erro de Adição ---")
    print(client.service.create_playlist(nome="Playlist Inexistente", user_id=99)) # Usuário não existe
    print(client.service.add_music_to_playlist(playlist_id=1, music_id=1)) # Duplicidade (música já na playlist)
    print(client.service.add_music_to_playlist(playlist_id=99, music_id=1)) # Playlist não existe
    print(client.service.add_music_to_playlist(playlist_id=1, music_id=99)) # Música não existe

    # --- NOVAS OPERAÇÕES DE CONSULTA (READ) ---
    print("\n--- Testando as Operações de Consulta (READ) ---")

    # 1. Listar todos os usuários
    print("\n-- Listando todos os usuários --")
    users = client.service.list_users()
    if users:
        for user in users:
            print(f"  Usuário ID: {user.id}, Nome: {user.nome}, Idade: {user.idade}")
    else:
        print("  Nenhum usuário encontrado.")

    # 2. Listar todas as músicas
    print("\n-- Listando todas as músicas --")
    musics = client.service.list_all_music()
    if musics:
        for music in musics:
            print(f"  Música ID: {music.id}, Nome: {music.nome}, Artista: {music.artista}")
    else:
        print("  Nenhuma música encontrada.")

    # 3. Listar playlists de um usuário (ex: user_id=1)
    print("\n-- Listando playlists do Usuário ID 1 (Alice) --")
    playlists_user1 = client.service.list_user_playlists(user_id=1)
    if playlists_user1:
        for pl in playlists_user1:
            print(f"  Playlist ID: {pl.id}, Nome: {pl.nome}, User_ID: {pl.user_id}")
    else:
        print("  Nenhuma playlist encontrada para o usuário ID 1.")
    
    print("\n-- Listando playlists do Usuário ID 99 (inexistente) --")
    playlists_user99 = client.service.list_user_playlists(user_id=99)
    if not playlists_user99:
        print("  Nenhuma playlist encontrada para o usuário ID 99 (esperado, lista vazia).")

    # 4. Listar músicas de uma playlist (ex: playlist_id=1)
    print("\n-- Listando músicas da Playlist ID 1 ('Favoritas da Alice') --")
    music_in_pl1 = client.service.list_playlist_music(playlist_id=1)
    if music_in_pl1:
        for music in music_in_pl1:
            print(f"  Música na Playlist ID 1: '{music.nome}' por '{music.artista}' (ID: {music.id})")
    else:
        print("  Nenhuma música encontrada na playlist ID 1.")
    
    print("\n-- Listando músicas da Playlist ID 99 (inexistente) --")
    music_in_pl99 = client.service.list_playlist_music(playlist_id=99)
    if not music_in_pl99:
        print("  Nenhuma música encontrada na playlist ID 99 (esperado, lista vazia).")

    # 5. Listar playlists que contêm uma música (ex: music_id=1)
    print("\n-- Listando playlists que contêm a Música ID 1 ('O Ritmo da Vida') --")
    playlists_with_music1 = client.service.list_playlists_by_music(music_id=1)
    if playlists_with_music1:
        for pl in playlists_with_music1:
            print(f"  Playlist com Música ID 1: ID {pl.id}, Nome: '{pl.nome}' (User_ID: {pl.user_id})")
    else:
        print("  Nenhuma playlist encontrada contendo a música ID 1.")

    print("\n-- Listando playlists que contêm a Música ID 99 (inexistente) --")
    playlists_with_music99 = client.service.list_playlists_by_music(music_id=99)
    if not playlists_with_music99:
        print("  Nenhuma playlist encontrada contendo a música ID 99 (esperado, lista vazia).")

except Fault as f:
    # Captura erros específicos do SOAP (falhas retornadas pelo servidor).
    print(f"❌ Erro SOAP (Fault): {f.message}")
except Exception as e:
    # Captura quaisquer outros erros que possam ocorrer (ex: problemas de conexão, URL errada).
    print(f"❌ Ocorreu um erro geral: {e}")
    print("Certifique-se de que o servidor SOAP esteja rodando e acessível na porta 8000.")
