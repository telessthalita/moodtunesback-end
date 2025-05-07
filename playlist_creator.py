import os
import random
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

MOOD_THERAPY = {
    "triste": {
        "genres": ["sad indie", "indie folk", "indie pop"],
        "filters": {"target_valence": 0.3, "target_energy": 0.4, "max_popularity": 70}
    },
    "ansioso": {
        "genres": ["ambient", "lofi", "jazz piano"],
        "filters": {"target_tempo": (60, 90), "target_mode": 0}
    },
    "feliz": {
        "genres": ["funk", "disco", "dance pop"],
        "filters": {"target_danceability": 0.85, "min_energy": 0.7}
    },
    "cansado": {
        "genres": ["chillhop", "dream pop", "slowed"],
        "filters": {"target_energy": 0.2, "target_valence": 0.3}
    }
}

def create_playlist_based_on_mood(mood, sp):
    therapy = MOOD_THERAPY.get(mood, MOOD_THERAPY["triste"])
    user_id = sp.current_user()["id"]
    
    tracks = []
    for genre in therapy["genres"]:
        results = sp.recommendations(
            seed_genres=[genre],
            limit=15,
            **therapy["filters"]
        )
        tracks.extend([track["uri"] for track in results["tracks"]])
    
    random.shuffle(tracks)
    unique_tracks = list(set(tracks))[:20]
    
    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"MoodTunes • {mood.capitalize()} • {datetime.now().strftime('%d/%m')}",
        public=False,
        description=f"Playlist terapêutica para {mood}"
    )
    
    sp.playlist_add_items(playlist["id"], unique_tracks)
    return playlist["external_urls"]["spotify"]