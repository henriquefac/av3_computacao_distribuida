# IMPORTS
from spyne.service import ServiceBase
from spyne.application import Application
from spyne.decorator import srpc
from spyne.protocol.soap import Soap12
from spyne.model.primitive import Integer, String, Unicode
from spyne.model.complex import ComplexModel
from spyne.server.wsgi import WsgiApplication

import sqlite3
import os

# bando de dados
DATABASE = "data/database.db"

# criar tabelas

# users: ip, nome, idade
# music: id, nome, artista
# playlist: id, nome, user_id(foreignkey)
# playlist_music: playlist_id(foreignkey), user_id(foreignkey), primarykey(playlist_id, music_id)

def create_tables():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        print("Criando tabelas...")
        
        # tabela usuários
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER
        )
        """)

        print("Tabela de usuários criada!")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS music (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT NOT NULL,
            artista TEXT
        )
        """)

        print("Tabela de musicas criada")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS playlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        print("Tabela de playlists criada")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS playlist_music (
            playlist_id INTEGER NOT NULL,
            music_id INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, music_id),
            FOREIGN KEY (playlist_id) REFERENCES playlist(id),
            FOREIGN KEY (music_id) REFERENCES music(id)
        )
        """)

        conn.commit()
        print("Tabelas criadas com sucesso")

    except sqlite3.Error as e:
        print(f"Erro: Erro ao criar tabelas: {e}")
    finally:
        if conn:
            conn.close()

if not os.path.exists(DATABASE):
    print(f"Databae '{DATABASE}' não existe, criando database e tabelas.")
    create_tables()
else:
    print(f"Database '{DATABASE}' já existe, criando tabelas.")
    create_tables()

# representa usuários
class User(ComplexModel):
    id = Integer(min_occurs=0)
    nome = Unicode
    idade = Integer

# representa musica
class Music(ComplexModel):
    id = Integer(min_occurs=0)
    nome = Unicode
    artista = Unicode

# representa playlist
class Playlist(ComplexModel):
    id = Integer(min_occurs=0)
    nome = Unicode
    user_id = Integer


class CorsService(ServiceBase):
    origin = '*'  

def _on_method_return_object(ctx):
    ctx.transport.resp_headers['Access-Control-Allow-Origin'] = CorsService.origin
    ctx.transport.resp_headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    ctx.transport.resp_headers['Access-Control-Allow-Headers'] = 'Content-Type, SOAPAction'



def _on_method_call(ctx):
    if ctx.transport.req_env['REQUEST_METHOD'] == 'OPTIONS':
        ctx.out_string = b''
        ctx.transport.resp_headers['Access-Control-Allow-Origin'] = CorsService.origin
        ctx.transport.resp_headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        ctx.transport.resp_headers['Access-Control-Allow-Headers'] = 'Content-Type, SOAPAction'
        ctx.transport.resp_status = 200
        ctx.transport.close()
        raise Exception("CORS preflight response")


# 🔗 Conectando os listeners aos eventos do Spyne
CorsService.event_manager.add_listener('method_return_object', _on_method_return_object)
CorsService.event_manager.add_listener('method_call', _on_method_call)




class Servico(CorsService):
    # adicionar usuário com nome e idade a tabela users
    @srpc(Unicode, Integer, _returns=Unicode)
    def add_user(nome, idade):
        con = None
        try:
            con = sqlite3.connect(DATABASE)
            cursor = con.cursor()
            cursor.execute("INSERT INTO users (nome, idade) VALUES (?, ?)", (nome, idade))
            con.commit()
            print(f"Usuário '{nome}' adicionado")
            return f"Usuário '{nome}' adicionado com sucesso"
        except sqlite3.Error as e:
            print(f"Erro ao adicionar usuário: {e}")
            return f"Erro ao adicionar o usuário {nome}: {e}"
        finally:
            if con:
                con.close()
    
    # Adicionar musica para a tabela de musicas

    @srpc(Unicode, Unicode, _returns=Unicode)
    def add_music(nome, artista):
        con = None
        try:
            con = sqlite3.connect(DATABASE)
            cursor = con.cursor()
            cursor.execute("INSERT INTO music (nome, artista) VALUES (?, ?)", (nome, artista))
            con.commit()
            print(f"Musica '{nome}' adicionada")
            return f"Musica '{nome}' adicionada com sucesso"
        except sqlite3.Error as e:
            print(f"Erro ao adicionar música: {e}")
            return f"Erro ao adicionar música {nome}: {e}"
        finally:
            if con:
                con.close()


    @srpc(Unicode, Integer, _returns=Unicode)
    def create_playlist(nome, user_id):
        con = None
        try:
            con = sqlite3.connect(DATABASE)
            cursor = con.cursor()

            # encontrar usuário criador da playlist
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            user_exists = cursor.fetchone()
            if not user_exists:
                return f"Error ao buscar usuário de id '{user_id}': não encontrado"
            
            # com o id do usuário confirmado, adicionar playlist com foreign key
            cursor.execute("INSERT INTO playlist (nome, user_id) VALUES (?, ?)", (nome, user_id))
            con.commit()
            print(f"Playlist '{nome}' foi criada com sucesso, associada ao usuário de id '{user_id}'")
            return f"Sucesso ao criar playlist '{nome}' associada ao usuário de id '{user_id}'"

        except sqlite3.Error as e:
            print(f"Erro ao adicionar a playlist '{nome}': {e}")
            return f"Erro ao adicionar a playlist '{nome}'"
        finally:
            if con:
                con.close()


    # adicionar música a playlist
    @srpc(Integer, Integer, _returns=Unicode)
    def add_music_to_playlist(playlist_id, music_id):
        con = None
        try:
            con = sqlite3.connect(DATABASE)
            cursor = con.cursor()

            # confirmar que a playlist existe
            cursor.execute("SELECT id FROM playlist WHERE id = ?", (playlist_id,))
            playlist_exist = cursor.fetchone()

            if not playlist_exist:
                return f"Erro ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}': playlist não existe"
            print("Feito: 1")
            # confirmar que musica existe
            cursor.execute("SELECT id FROM music WHERE id = ?", (music_id,))
            music_exist = cursor.fetchone()

            if not music_exist:
                return f"Erro ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}': musica não existe"
            print("Feito: 2")
            cursor.execute("INSERT INTO playlist_music (playlist_id, music_id) VALUES (?, ?)", (playlist_id, music_id))
            con.commit()
            print("Feito: 3")
            print(f"Sucesso ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}'")
            return f"Música '{music_id}' adicionada a '{playlist_id}' com sucessso"
        except sqlite3.Error as e:
            print(f"Erro ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}': {e}")
            return f"Erro ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}'"
        except ValueError as e:
            print(f"Erro: {e}")
            return f"Erro: {e}"
        finally:
            if con:
                con.close()
    # crud

    @srpc(_returns=User.customize(max_occurs='unbounded'))
    def list_users(): # Renomeado para consistência (list_all_users no exemplo anterior)
        """Lista todos os usuários cadastrados no serviço."""
        conn = None
        user_list = []
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute("SELECT id, nome, idade FROM users")
            rows = cursor.fetchall()
            for row in rows:
                user_list.append(User(id=row[0], nome=row[1], idade=row[2]))
            print(f"DEBUG: Listados {len(user_list)} usuários.") # Corrigido log de depuração
            return user_list
        except sqlite3.Error as e:
            print(f"ERRO: Erro ao listar usuários: {e}")
            return [] # Retorna lista vazia em caso de erro
        finally:
            if conn:
                conn.close()

    @srpc(_returns=Music.customize(max_occurs='unbounded'))
    def list_all_music():
        """Lista todas as músicas cadastradas no serviço."""
        con = None
        music_list = []
        try:
            con = sqlite3.connect(DATABASE)
            cursor = con.cursor()

            cursor.execute("SELECT id, nome, artista FROM music")
            rows = cursor.fetchall()

            for row in rows:
                music_list.append(Music(id=row[0], nome=row[1], artista=row[2]))
            print(f"DEBUG: Foram listadas {len(music_list)} músicas.") # Corrigido log de depuração
            # Retornar a lista de objetos, não uma string de sucesso
            return music_list
        except sqlite3.Error as e:
            print(f"ERRO: Erro ao listar músicas: {e}")
            return []
        finally:
            if con:
                con.close()

    @srpc(Integer, _returns=Playlist.customize(max_occurs='unbounded'))
    def list_user_playlists(user_id):
        """Lista todas as playlists de um determinado usuário."""
        conn = None
        playlist_list = []
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            # Corrigido SELECT da tabela 'users'
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            user_exist = cursor.fetchone()
            if not user_exist:
                print(f"DEBUG: Erro: usuário '{user_id}' não existe para listar playlists.")
                return []

            cursor.execute("SELECT id, nome, user_id FROM playlist WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            for row in rows:
                playlist_list.append(Playlist(id=row[0], nome=row[1], user_id=row[2]))
            print(f"DEBUG: Listados {len(playlist_list)} playlists do usuário '{user_id}'.")
            return playlist_list
        except sqlite3.Error as e:
            print(f"ERRO: Erro ao listar playlists do usuário {user_id}: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    # 5. Listar os dados de todas as músicas de uma determinada playlist
    @srpc(Integer, _returns=Music.customize(max_occurs='unbounded')) # Retorna lista de Music para uma playlist
    def list_playlist_music(playlist_id): # Nome da função corrigido para o esperado no cliente
        """Lista todas as músicas de uma playlist específica."""
        conn = None
        music_in_playlist = []
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM playlist WHERE id = ?", (playlist_id,))
            playlist_exists = cursor.fetchone()
            if not playlist_exists:
                print(f"DEBUG: Playlist ID {playlist_id} não encontrada para listar músicas.")
                return []

            cursor.execute("""
                SELECT m.id, m.nome, m.artista
                FROM music m
                JOIN playlist_music pm ON m.id = pm.music_id
                WHERE pm.playlist_id = ?
            """, (playlist_id,))
            rows = cursor.fetchall()
            for row in rows:
                music_in_playlist.append(Music(id=row[0], nome=row[1], artista=row[2]))
            print(f"DEBUG: Listadas {len(music_in_playlist)} músicas para a playlist ID {playlist_id}.")
            return music_in_playlist
        except sqlite3.Error as e:
            print(f"ERRO: Erro ao listar músicas da playlist {playlist_id}: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @srpc(Integer, _returns=Playlist.customize(max_occurs='unbounded'))
    def list_playlists_by_music(music_id):
        """Lista todas as playlists que contêm uma música específica."""
        conn = None
        playlists_containing_music = []
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM music WHERE id = ?", (music_id,))
            music_exists = cursor.fetchone()
            if not music_exists:
                print(f"DEBUG: Música ID {music_id} não encontrada para listar playlists.")
                return []

            cursor.execute("""
                SELECT p.id, p.nome, p.user_id
                FROM playlist p
                JOIN playlist_music pm ON p.id = pm.playlist_id
                WHERE pm.music_id = ?
            """, (music_id,))
            rows = cursor.fetchall()
            for row in rows:
                playlists_containing_music.append(Playlist(id=row[0], nome=row[1], user_id=row[2]))
            print(f"DEBUG: Listadas {len(playlists_containing_music)} playlists para a música ID {music_id}.")
            return playlists_containing_music
        except sqlite3.Error as e:
            print(f"ERRO: Erro ao listar playlists pela música {music_id}: {e}")
            return []
        finally:
            if conn:
                conn.close()
application = Application([Servico],
                tns="servico.spyne.python",
                in_protocol=Soap12(validator="lxml"),
                out_protocol=Soap12())

wsgi_app = WsgiApplication(application)















