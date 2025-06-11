from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

app = FastAPI()

DATABASE = "data/database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class UserBase(BaseModel):
    nome: str
    idade: Optional[int] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class MusicBase(BaseModel):
    nome: str
    artista: Optional[str] = None

class Music(MusicBase):
    id: int

    class Config:
        from_attributes = True

class PlaylistBase(BaseModel):
    nome: str
    user_id: int

class Playlist(PlaylistBase):
    id: int
    musics: List[Music] = []

    class Config:
        from_attributes = True

# User endpoints
@app.post("/users/", response_model=User)
def create_user(user: UserBase):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (nome, idade) VALUES (?, ?)",
            (user.nome, user.idade)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return User(id=user_id, **user.dict())
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(**dict(user))
        raise HTTPException(status_code=404, detail="User not found")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/users/", response_model=List[User])
def list_users():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return [User(**dict(user)) for user in users]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

# Music endpoints
@app.post("/music/", response_model=Music)
def create_music(music: MusicBase):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO music (nome, artista) VALUES (?, ?)",
            (music.nome, music.artista)
        )
        conn.commit()
        music_id = cursor.lastrowid
        return Music(id=music_id, **music.dict())
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/music/{music_id}", response_model=Music)
def get_music(music_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM music WHERE id = ?", (music_id,))
        music = cursor.fetchone()
        if music:
            return Music(**dict(music))
        raise HTTPException(status_code=404, detail="Music not found")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/music/", response_model=List[Music])
def list_music():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM music")
        musics = cursor.fetchall()
        return [Music(**dict(music)) for music in musics]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

# Playlist endpoints
@app.post("/playlists/", response_model=Playlist)
def create_playlist(playlist: PlaylistBase):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO playlist (nome, user_id) VALUES (?, ?)",
            (playlist.nome, playlist.user_id)
        )
        conn.commit()
        playlist_id = cursor.lastrowid
        return Playlist(id=playlist_id, **playlist.dict())
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/playlists/{playlist_id}", response_model=Playlist)
def get_playlist(playlist_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM playlist WHERE id = ?", (playlist_id,))
        playlist = cursor.fetchone()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # Get musics in playlist
        cursor.execute("""
            SELECT m.* FROM music m
            JOIN playlist_music pm ON m.id = pm.music_id
            WHERE pm.playlist_id = ?
        """, (playlist_id,))
        musics = cursor.fetchall()

        return Playlist(
            **dict(playlist),
            musics=[Music(**dict(music)) for music in musics]
        )
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/users/{user_id}/playlists/", response_model=List[Playlist])
def list_user_playlists(user_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM playlist WHERE user_id = ?", (user_id,))
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

            result.append(Playlist(
                **dict(playlist),
                musics=[Music(**dict(music)) for music in musics]
            ))

        return result
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.post("/playlists/{playlist_id}/music/{music_id}", response_model=Playlist)
def add_music_to_playlist(playlist_id: int, music_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO playlist_music (playlist_id, music_id) VALUES (?, ?)",
            (playlist_id, music_id)
        )
        conn.commit()
        
        # Return updated playlist
        return get_playlist(playlist_id)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 