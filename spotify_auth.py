from spotipy.oauth2 import SpotifyOAuth
import os
from flask import jsonify

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-private playlist-modify-private playlist-modify-public",
        cache_path=".spotify_cache"
    )

def get_token_from_callback(code):
    try:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.get_access_token(code, as_dict=True)
        
        if not token_info or 'access_token' not in token_info:
            raise Exception("Resposta inválida do Spotify")
            
        return token_info
    except Exception as e:
        print(f"ERRO NA TROCA DO TOKEN: {str(e)}")
        raise