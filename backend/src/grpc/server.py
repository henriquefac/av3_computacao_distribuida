import grpc
from concurrent import futures
import sqlite3
import os
from typing import List, Optional

# Import generated gRPC code
import music_service_pb2
import music_service_pb2_grpc

DATABASE = "data/database.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER
        );

        CREATE TABLE IF NOT EXISTS music (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            artista TEXT
        );

        CREATE TABLE IF NOT EXISTS playlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS playlist_music (
            playlist_id INTEGER NOT NULL,
            music_id INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, music_id),
            FOREIGN KEY (playlist_id) REFERENCES playlist (id),
            FOREIGN KEY (music_id) REFERENCES music (id)
        );
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

class MusicServiceServicer(music_service_pb2_grpc.MusicServiceServicer):
    def CreateUser(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (nome, idade) VALUES (?, ?)",
                (request.nome, request.idade)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return music_service_pb2.User(
                id=user_id,
                nome=request.nome,
                idade=request.idade
            )
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.User()
        finally:
            conn.close()

    def GetUser(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (request.id,))
            user = cursor.fetchone()
            if user:
                return music_service_pb2.User(
                    id=user["id"],
                    nome=user["nome"],
                    idade=user["idade"]
                )
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return music_service_pb2.User()
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.User()
        finally:
            conn.close()

    def ListUsers(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            return music_service_pb2.ListUsersResponse(
                users=[
                    music_service_pb2.User(
                        id=user["id"],
                        nome=user["nome"],
                        idade=user["idade"]
                    )
                    for user in users
                ]
            )
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.ListUsersResponse()
        finally:
            conn.close()

    def CreateMusic(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO music (nome, artista) VALUES (?, ?)",
                (request.nome, request.artista)
            )
            conn.commit()
            music_id = cursor.lastrowid
            return music_service_pb2.Music(
                id=music_id,
                nome=request.nome,
                artista=request.artista
            )
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.Music()
        finally:
            conn.close()

    def GetMusic(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM music WHERE id = ?", (request.id,))
            music = cursor.fetchone()
            if music:
                return music_service_pb2.Music(
                    id=music["id"],
                    nome=music["nome"],
                    artista=music["artista"]
                )
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Music not found")
            return music_service_pb2.Music()
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.Music()
        finally:
            conn.close()

    def ListMusic(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM music")
            musics = cursor.fetchall()
            return music_service_pb2.ListMusicResponse(
                musics=[
                    music_service_pb2.Music(
                        id=music["id"],
                        nome=music["nome"],
                        artista=music["artista"]
                    )
                    for music in musics
                ]
            )
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.ListMusicResponse()
        finally:
            conn.close()

    def CreatePlaylist(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO playlist (nome, user_id) VALUES (?, ?)",
                (request.nome, request.user_id)
            )
            conn.commit()
            playlist_id = cursor.lastrowid
            return music_service_pb2.Playlist(
                id=playlist_id,
                nome=request.nome,
                user_id=request.user_id
            )
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.Playlist()
        finally:
            conn.close()

    def GetPlaylist(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM playlist WHERE id = ?", (request.id,))
            playlist = cursor.fetchone()
            if not playlist:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist not found")
                return music_service_pb2.Playlist()

            # Get musics in playlist
            cursor.execute("""
                SELECT m.* FROM music m
                JOIN playlist_music pm ON m.id = pm.music_id
                WHERE pm.playlist_id = ?
            """, (request.id,))
            musics = cursor.fetchall()

            return music_service_pb2.Playlist(
                id=playlist["id"],
                nome=playlist["nome"],
                user_id=playlist["user_id"],
                musics=[
                    music_service_pb2.Music(
                        id=music["id"],
                        nome=music["nome"],
                        artista=music["artista"]
                    )
                    for music in musics
                ]
            )
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.Playlist()
        finally:
            conn.close()

    def ListUserPlaylists(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM playlist WHERE user_id = ?", (request.user_id,))
            playlists = cursor.fetchall()
            
            result = []
            for playlist in playlists:
                # Get musics for each playlist
                cursor.execute("""
                    SELECT m.* FROM music m
                    JOIN playlist_music pm ON m.id = pm.music_id
                    WHERE pm.playlist_id = ?
                """, (playlist["id"],))
                musics = cursor.fetchall()

                result.append(music_service_pb2.Playlist(
                    id=playlist["id"],
                    nome=playlist["nome"],
                    user_id=playlist["user_id"],
                    musics=[
                        music_service_pb2.Music(
                            id=music["id"],
                            nome=music["nome"],
                            artista=music["artista"]
                        )
                        for music in musics
                    ]
                ))

            return music_service_pb2.ListPlaylistsResponse(playlists=result)
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.ListPlaylistsResponse()
        finally:
            conn.close()

    def AddMusicToPlaylist(self, request, context):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO playlist_music (playlist_id, music_id) VALUES (?, ?)",
                (request.playlist_id, request.music_id)
            )
            conn.commit()
            
            # Return updated playlist
            return self.GetPlaylist(
                music_service_pb2.GetPlaylistRequest(id=request.playlist_id),
                context
            )
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return music_service_pb2.Playlist()
        finally:
            conn.close()

def serve():
    # Initialize database
    init_db()
    
    # Create server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    music_service_pb2_grpc.add_MusicServiceServicer_to_server(
        MusicServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 