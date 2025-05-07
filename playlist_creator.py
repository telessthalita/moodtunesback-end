import random
from datetime import datetime
from spotipy.exceptions import SpotifyException

MOOD_PROFILES = {
    "feliz": {
        "genres": ["pop", "dance", "indie-pop", "funk"],
        "params": {
            "valence": 0.8,
            "energy": 0.7,
            "danceability": 0.7,
            "tempo": (100, 140)
        },
        "description": "Playlist energética para elevar seu espírito! ✨"
    },
    "triste": {
        "genres": ["acoustic", "piano", "singer-songwriter", "chill"],
        "params": {
            "valence": 0.3,
            "energy": 0.3,
            "acousticness": 0.7,
            "tempo": (60, 100)
        },
        "description": "Músicas para acompanhar seus sentimentos 🫂"
    },
    "focada": {
        "genres": ["classical", "ambient", "jazz", "instrumental"],
        "params": {
            "instrumentalness": 0.7,
            "energy": 0.4,
            "valence": 0.5,
            "tempo": (80, 110)
        },
        "description": "Concentração máxima com essas seleções 🎯"
    },
    "ansiosa": {
        "genres": ["ambient", "new-age", "meditation", "soundtrack"],
        "params": {
            "valence": 0.4,
            "energy": 0.2,
            "acousticness": 0.6,
            "tempo": (60, 90)
        },
        "description": "Sons relaxantes para acalmar 🌿"
    }
}

def create_playlist_based_on_mood(mood, sp):
    try:
        mood_profile = MOOD_PROFILES.get(mood.lower(), MOOD_PROFILES["feliz"])
        user = sp.current_user()
        user_id = user["id"]
        
        available_genres = sp.recommendation_genre_seeds()['genres']
        valid_genres = [g for g in mood_profile["genres"] if g in available_genres][:2]
        
        if not valid_genres:
            valid_genres = ["pop", "acoustic"]

        recommendations = sp.recommendations(
            seed_genres=valid_genres,
            limit=30,
            **{k: v for k, v in mood_profile["params"].items() if not isinstance(v, tuple)}
        )
        
        if "tempo" in mood_profile["params"]:
            min_tempo, max_tempo = mood_profile["params"]["tempo"]
            recommendations["tracks"] = [
                t for t in recommendations["tracks"]
                if min_tempo <= t["tempo"] <= max_tempo
            ][:20]
        
        track_uris = [track["uri"] for track in recommendations["tracks"]]
        
        playlist_name = f"{mood.capitalize()} Vibes - MoodTunes"
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"{mood_profile['description']} ({datetime.now().strftime('%d/%m/%Y')})"
        )
        
        sp.playlist_add_items(playlist["id"], track_uris)
        return playlist["external_urls"]["spotify"]
        
    except SpotifyException as e:
        raise Exception(f"Erro no Spotify: {e.msg}")
    except Exception as e:
        raise Exception(f"Erro ao criar playlist: {str(e)}")