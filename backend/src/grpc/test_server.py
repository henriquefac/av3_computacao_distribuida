import unittest
import grpc
import music_service_pb2
import music_service_pb2_grpc
import server
import threading
import time

class TestMusicService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the server in a separate thread
        cls.server_thread = threading.Thread(target=server.serve)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Wait for server to start

        # Create a channel and stub
        cls.channel = grpc.insecure_channel('localhost:50051')
        cls.stub = music_service_pb2_grpc.MusicServiceStub(cls.channel)

    def test_create_user(self):
        # Test creating a user
        request = music_service_pb2.CreateUserRequest(nome="Test User", idade=25)
        response = self.stub.CreateUser(request)
        self.assertIsNotNone(response.id)
        self.assertEqual(response.nome, "Test User")
        self.assertEqual(response.idade, 25)

    def test_create_music(self):
        # Test creating a music
        request = music_service_pb2.CreateMusicRequest(nome="Test Music", artista="Test Artist")
        response = self.stub.CreateMusic(request)
        self.assertIsNotNone(response.id)
        self.assertEqual(response.nome, "Test Music")
        self.assertEqual(response.artista, "Test Artist")

    def test_create_playlist(self):
        # First create a user
        user_request = music_service_pb2.CreateUserRequest(nome="Playlist User", idade=30)
        user_response = self.stub.CreateUser(user_request)

        # Test creating a playlist
        request = music_service_pb2.CreatePlaylistRequest(nome="Test Playlist", user_id=user_response.id)
        response = self.stub.CreatePlaylist(request)
        self.assertIsNotNone(response.id)
        self.assertEqual(response.nome, "Test Playlist")
        self.assertEqual(response.user_id, user_response.id)

    def test_add_music_to_playlist(self):
        # Create a user
        user_request = music_service_pb2.CreateUserRequest(nome="Music User", idade=35)
        user_response = self.stub.CreateUser(user_request)

        # Create a playlist
        playlist_request = music_service_pb2.CreatePlaylistRequest(nome="Music Playlist", user_id=user_response.id)
        playlist_response = self.stub.CreatePlaylist(playlist_request)

        # Create a music
        music_request = music_service_pb2.CreateMusicRequest(nome="Playlist Music", artista="Playlist Artist")
        music_response = self.stub.CreateMusic(music_request)

        # Test adding music to playlist
        request = music_service_pb2.AddMusicToPlaylistRequest(
            playlist_id=playlist_response.id,
            music_id=music_response.id
        )
        response = self.stub.AddMusicToPlaylist(request)
        self.assertEqual(response.id, playlist_response.id)
        self.assertEqual(len(response.musics), 1)
        self.assertEqual(response.musics[0].id, music_response.id)

if __name__ == '__main__':
    unittest.main() 