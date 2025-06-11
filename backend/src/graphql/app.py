# servidor feito com python e strawberry

# imports
import strawberry
from typing import List, Optional
from fastapi import FastAPI, Depends
from strawberry.asgi import GraphQL
from strawberry.fastapi import GraphQLRouter
import json
import os

import sqlite3

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
    musicas: Optional[List[Music]] = None

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

# Data storage
class DataStore:
    def __init__(self):
        self.users = []
        self.musics = []
        self.playlists = []
        self.playlist_musics = {}  # playlist_id -> [music_id]
        self.load_data()

    def load_data(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        try:
            with open(os.path.join(data_dir, 'users.json'), 'r') as f:
                self.users = json.load(f)
            with open(os.path.join(data_dir, 'musics.json'), 'r') as f:
                self.musics = json.load(f)
            with open(os.path.join(data_dir, 'playlists.json'), 'r') as f:
                self.playlists = json.load(f)
            with open(os.path.join(data_dir, 'playlist_musics.json'), 'r') as f:
                self.playlist_musics = json.load(f)
        except FileNotFoundError:
            # Initialize with empty data if files don't exist
            self.save_data()

    def save_data(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        with open(os.path.join(data_dir, 'users.json'), 'w') as f:
            json.dump(self.users, f)
        with open(os.path.join(data_dir, 'musics.json'), 'w') as f:
            json.dump(self.musics, f)
        with open(os.path.join(data_dir, 'playlists.json'), 'w') as f:
            json.dump(self.playlists, f)
        with open(os.path.join(data_dir, 'playlist_musics.json'), 'w') as f:
            json.dump(self.playlist_musics, f)

# GraphQL Query and Mutation types
@strawberry.type
class Query:
    @strawberry.field
    def list_users(self) -> List[User]:
        return [User(**user) for user in data_store.users]

    @strawberry.field
    def list_all_music(self) -> List[Music]:
        return [Music(**music) for music in data_store.musics]

    @strawberry.field
    def list_user_playlists(self, user_id: int) -> List[Playlist]:
        user_playlists = [p for p in data_store.playlists if p['user_id'] == user_id]
        return [
            Playlist(
                **p,
                musicas=[Music(**m) for m in data_store.musics 
                        if m['id'] in data_store.playlist_musics.get(p['id'], [])]
            )
            for p in user_playlists
        ]

    @strawberry.field
    def list_playlist_music(self, playlist_id: int) -> List[Music]:
        music_ids = data_store.playlist_musics.get(playlist_id, [])
        return [Music(**m) for m in data_store.musics if m['id'] in music_ids]

    @strawberry.field
    def list_playlists_by_music(self, music_id: int) -> List[Playlist]:
        playlists_with_music = [
            p for p in data_store.playlists
            if music_id in data_store.playlist_musics.get(p['id'], [])
        ]
        return [
            Playlist(
                **p,
                musicas=[Music(**m) for m in data_store.musics 
                        if m['id'] in data_store.playlist_musics.get(p['id'], [])]
            )
            for p in playlists_with_music
        ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_user(self, nome: str, idade: int) -> User:
        user_id = len(data_store.users) + 1
        user = {"id": user_id, "nome": nome, "idade": idade}
        data_store.users.append(user)
        data_store.save_data()
        return User(**user)

    @strawberry.mutation
    def add_music(self, nome: str, artista: str) -> Music:
        music_id = len(data_store.musics) + 1
        music = {"id": music_id, "nome": nome, "artista": artista}
        data_store.musics.append(music)
        data_store.save_data()
        return Music(**music)

    @strawberry.mutation
    def create_playlist(self, nome: str, user_id: int) -> Playlist:
        if not any(u['id'] == user_id for u in data_store.users):
            raise ValueError("User not found")
        
        playlist_id = len(data_store.playlists) + 1
        playlist = {"id": playlist_id, "nome": nome, "user_id": user_id}
        data_store.playlists.append(playlist)
        data_store.playlist_musics[playlist_id] = []
        data_store.save_data()
        return Playlist(**playlist, musicas=[])

    @strawberry.mutation
    def add_music_to_playlist(self, playlist_id: int, music_id: int) -> Playlist:
        if not any(p['id'] == playlist_id for p in data_store.playlists):
            raise ValueError("Playlist not found")
        if not any(m['id'] == music_id for m in data_store.musics):
            raise ValueError("Music not found")
        if music_id in data_store.playlist_musics.get(playlist_id, []):
            raise ValueError("Music already in playlist")

        if playlist_id not in data_store.playlist_musics:
            data_store.playlist_musics[playlist_id] = []
        data_store.playlist_musics[playlist_id].append(music_id)
        data_store.save_data()

        playlist = next(p for p in data_store.playlists if p['id'] == playlist_id)
        return Playlist(
            **playlist,
            musicas=[Music(**m) for m in data_store.musics 
                    if m['id'] in data_store.playlist_musics[playlist_id]]
        )

# Initialize FastAPI app
app = FastAPI()

# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Add GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Add root endpoint
@app.get("/")
async def root():
    return {"message": "GraphQL server is running"}

# Initialize data store
data_store = DataStore()

