import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv() 

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = "user-read-private playlist-modify-private playlist-modify-public"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    show_dialog=True,
)

def get_auth_url():
    return sp_oauth.get_authorize_url()

def get_token_from_callback(code):
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)
    return sp  

def get_valid_spotify_client(token_info):
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp, token_info
