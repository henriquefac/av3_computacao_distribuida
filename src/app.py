# IMPORTS
from spyne.service import ServiceBase
from spyne.application import Application
from spyne.decorator import srpc
from spyne.protocol.soap import Soap12
from spyne.model.primitive import Integer, String, Unicode
from spyne.server.wsgi import WsgiApplication

import sqlite3
import os

# bando de dados
DATABASE = "database.db"

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

class Servico(ServiceBase):
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
            
            # confirmar que musica existe
            cursor.execute("SELECT id FROM music WHERE id = ?", (music_id,))
            music_exist = cursor.fetchone()

            if not music_exist:
                return f"Erro ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}': musica não existe"
            
            cursor.execute("INSERT INTO playlist_music (playlist_id, music_id) VALUES (?, ?)", (playlist_id, music_id))
            con.commit()
            print(f"Sucesso ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}'")
            return f"Música '{music_id}' adicionada a '{playlist_id}' com sucessso"
        except sqlite3.IntegrityError as e:
            print(f"Erro de integridade ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}': {e}")
            return f"Erro de integridade ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}': {e}"
        except sqlite3.Error as e:
            print(f"Erro ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}': {e}")
            return f"Erro ao adicionar musica de id '{music_id}' para a playlist de id '{playlist_id}'"
        finally:
            if con:
                con.close()

application = Application([Servico],
                tns="servico.spyne.python",
                in_protocol=Soap12(validator="lxml"),
                out_protocol=Soap12())

wsgi_app = WsgiApplication(application)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()















