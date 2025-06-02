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
    # Imprime os métodos que o Zeep descobriu. Útil para verificar se o WSDL foi lido corretamente.
    print(client.service)

    # --- Testando as operações de Adição (CREATE) ---

    print("\n--- Adicionando Usuários ---")
    # Adiciona alguns usuários. O ID será gerado automaticamente pelo SQLite.
    print(client.service.add_user(nome="Alice Silva", idade=25))
    print(client.service.add_user(nome="Bruno Costa", idade=30))
    print(client.service.add_user(nome="Carla Souza", idade=22))

    print("\n--- Adicionando Músicas ---")
    # Adiciona algumas músicas.
    print(client.service.add_music(nome="O Ritmo da Vida", artista="Banda Sonhos"))
    print(client.service.add_music(nome="Caminho do Sol", artista="Solo Perfeito"))
    print(client.service.add_music(nome="Noite Estrelada", artista="Cantor Desconhecido"))

    print("\n--- Criando Playlists ---")
    # Cria playlists para usuários existentes.
    # user_id=1 provavelmente será "Alice Silva"
    print(client.service.create_playlist(nome="Favoritas da Alice", user_id=1))
    # user_id=2 provavelmente será "Bruno Costa"
    print(client.service.create_playlist(nome="Hits de Rock do Bruno", user_id=2))
    # Tenta criar uma playlist para um usuário que não existe (user_id=99).
    print(client.service.create_playlist(nome="Playlist Inexistente", user_id=99)) # Deve retornar erro

    print("\n--- Adicionando Músicas a Playlists ---")
    # Adiciona músicas às playlists criadas.
    # Playlist ID 1 ("Favoritas da Alice"), Música ID 1 ("O Ritmo da Vida")
    print(client.service.add_music_to_playlist(playlist_id=1, music_id=1))
    # Playlist ID 1 ("Favoritas da Alice"), Música ID 2 ("Caminho do Sol")
    print(client.service.add_music_to_playlist(playlist_id=1, music_id=2))
    # Playlist ID 2 ("Hits de Rock do Bruno"), Música ID 3 ("Noite Estrelada")
    print(client.service.add_music_to_playlist(playlist_id=2, music_id=3))

    # Tenta adicionar a mesma música à mesma playlist novamente (deve retornar erro de integridade).
    print(client.service.add_music_to_playlist(playlist_id=1, music_id=1))

    # Tenta adicionar músicas ou playlists com IDs inexistentes.
    print(client.service.add_music_to_playlist(playlist_id=99, music_id=1)) # Playlist não existe
    print(client.service.add_music_to_playlist(playlist_id=1, music_id=99)) # Música não existe

except Fault as f:
    # Captura erros específicos do SOAP (falhas retornadas pelo servidor).
    print(f"❌ Erro SOAP (Fault): {f.message}")
except Exception as e:
    # Captura quaisquer outros erros que possam ocorrer (ex: problemas de conexão).
    print(f"❌ Ocorreu um erro geral: {e}")
    print("Certifique-se de que o servidor SOAP esteja rodando e acessível na porta 8000.")
