# servidor feito com python e strawberry

# imports
import strawberry
from typing import List, Optional
from fastapi import FastAPI, Depends
from strawberry.asgi import GraphQL

import sqlite3
import os

# bando de dados
DATABASE = "data/database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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

# definir tipos 


@strawberry.type
class User:
    id: int
    nome: str
    idade: Optional[int]

    @strawberry.field
    def playlist(self) -> Optional[List["Playlist"]]:
        conn = None
        playlist_data = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id, nome, user_id FROM playlist WHERE user_id = ?", (self.id,))
            playlist_data = cursor.fetchall()
            if len(playlist_data) == 0:
                print("Usuário não possui playlists associadas a ele.")
                return []
            print(f"Foram encontradas {len(playlist_data)} playlists associadas ao usuário {self.id}")
            return [Playlist(id=pl["id"], nome=pl["nome"], user_id=pl["user_id"]) for pl in playlist_data]
        except sqlite3.Error as e:
            print(f"Erro ao buscar as playlists associadas ao usuário {self.id}: {e}")
            return []
@strawberry.type
class Music:
    id: int
    nome: str
    artista: Optional[str]

@strawberry.type
class Playlist:
    id: int
    nome: str
    user_id: int

    # Busar dono da playlist
    @strawberry.field
    def user(self) -> Optional[User]:
        conn = None
        user_ = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id, nome, idade FROM users WHERE id = ?", (self.user_id,))
            data = cursor.fetchone()
            user_ = User(id=data["id"], nome=data["nome"], idade = data['idade'])
            print(f"Usuário dono da playlista foi buscado com sucesso")
            return user_
        except sqlite3.Error as e:
            print(f"Erro ao buscar usuário proprietário da playlist:{e}")
            return None
        finally:
            if conn:
                conn.close()

    # buscar músicas da playlist
    @strawberry.field
    def musics(self) -> Optional[List[Music]]:
        conn = None
        music_list = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""SELECT m.id, m.nome, m.artista FROM music m
            JOIN playlist_music pm ON m.id = pm.music_id
            WHERE pm.playlist_id = ?""", (self.id,))
            
            music_list = cursor.fetchall()
            if len(music_list):
                print(f"Playlista não possui nenhuma música associada")
                return []
            print(f"Foram listadas {len(music_list)} musicas na playlista '{self.id}'")
            return [Music(id=m["id"], nome = m["nome"], artista=m["artista"]) for m in music_list]
        except sqlite3.Error as e:
            print(f"Erro ao acessar as músicas da playlist")
            return []
        finally:
            if conn:
                conn.close()

