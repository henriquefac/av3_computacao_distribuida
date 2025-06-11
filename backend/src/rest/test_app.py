import unittest
from fastapi.testclient import TestClient
import app

class TestMusicAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app.app)

    def test_create_user(self):
        response = self.client.post("/users/", json={"nome": "Test User", "idade": 25})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["nome"], "Test User")
        self.assertEqual(data["idade"], 25)

    def test_create_music(self):
        response = self.client.post("/music/", json={"nome": "Test Music", "artista": "Test Artist"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["nome"], "Test Music")
        self.assertEqual(data["artista"], "Test Artist")

    def test_create_playlist(self):
        # First create a user
        user_response = self.client.post("/users/", json={"nome": "Playlist User", "idade": 30})
        user_id = user_response.json()["id"]

        # Test creating a playlist
        response = self.client.post("/playlists/", json={"nome": "Test Playlist", "user_id": user_id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["nome"], "Test Playlist")
        self.assertEqual(data["user_id"], user_id)

    def test_add_music_to_playlist(self):
        # Create a user
        user_response = self.client.post("/users/", json={"nome": "Music User", "idade": 35})
        user_id = user_response.json()["id"]

        # Create a playlist
        playlist_response = self.client.post("/playlists/", json={"nome": "Music Playlist", "user_id": user_id})
        playlist_id = playlist_response.json()["id"]

        # Create a music
        music_response = self.client.post("/music/", json={"nome": "Playlist Music", "artista": "Playlist Artist"})
        music_id = music_response.json()["id"]

        # Test adding music to playlist
        response = self.client.post(f"/playlists/{playlist_id}/music/{music_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], playlist_id)
        self.assertEqual(len(data["musics"]), 1)
        self.assertEqual(data["musics"][0]["id"], music_id)

if __name__ == '__main__':
    unittest.main() 