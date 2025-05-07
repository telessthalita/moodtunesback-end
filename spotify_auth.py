import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    raise ValueError("""
    Variáveis de ambiente necessárias não encontradas!
    Certifique-se de ter um arquivo .env com:
    SPOTIPY_CLIENT_ID=seu_client_id
    SPOTIPY_CLIENT_SECRET=seu_client_secret
    SPOTIPY_REDIRECT_URI=sua_redirect_uri
    """)

SCOPE = "user-read-private playlist-modify-private playlist-modify-public"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        cache_path=".spotify_cache"
    )

def get_auth_url():
    try:
        sp_oauth = create_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        print(f"Debug: URL de auth gerada - {auth_url}")  # Debug
        return auth_url
    except Exception as e:
        error_msg = f"Erro ao gerar URL de autenticação: {str(e)}"
        print(error_msg)
        raise Exception(error_msg) from e

def get_token_from_callback(code):
    try:
        sp_oauth = create_spotify_oauth()
        
        token_info = sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
        if not token_info:
            raise SpotifyException(400, "Resposta do token vazia", "Nenhum token retornado")
        
        access_token = token_info.get('access_token')
        if not access_token:
            raise SpotifyException(400, "Token inválido", "Access token não encontrado")
        
        sp = spotipy.Spotify(auth=access_token)
        user_info = sp.current_user()
        if not user_info or 'id' not in user_info:
            raise SpotifyException(401, "Autenticação falhou", "Não foi possível obter dados do usuário")
        
        return sp, token_info
        
    except SpotifyException as spotify_err:
        print(f"Erro na API Spotify: {spotify_err}")
        raise
    except Exception as general_err:
        print(f"Erro inesperado: {general_err}")
        raise