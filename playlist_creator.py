import random
from datetime import datetime

MOOD_PROFILES = {
    "feliz": {
        "genres": ["pop", "dance", "indie-pop", "funk", "disco"],
        "params": {
            "valence": 0.8,
            "energy": 0.7,
            "danceability": 0.7,
            "tempo": (120, 140)
        },
        "description": "Playlist energética para elevar seu espírito! ✨"
    },
    "triste": {
        "genres": ["sad", "acoustic", "piano", "singer-songwriter"],
        "params": {
            "valence": 0.2,
            "energy": 0.3,
            "acousticness": 0.8,
            "tempo": (60, 90)
        },
        "description": "Músicas para acompanhar seus sentimentos e trazer conforto 🫂"
    },
    "focada": {
        "genres": ["classical", "ambient", "jazz", "post-rock"],
        "params": {
            "instrumentalness": 0.8,
            "energy": 0.4,
            "valence": 0.5,
            "tempo": (80, 100)
        },
        "description": "Concentração máxima com essas seleções instrumentais 🎯"
    },
    "ansiosa": {
        "genres": ["ambient", "lofi", "new-age", "meditation"],
        "params": {
            "valence": 0.4,
            "energy": 0.2,
            "acousticness": 0.7,
            "tempo": (60, 80)
        },
        "description": "Sons relaxantes para acalmar a mente e o coração 🌿"
    },
    "animada": {
        "genres": ["edm", "rock", "hip-hop", "funk"],
        "params": {
            "valence": 0.9,
            "energy": 0.9,
            "danceability": 0.8,
            "tempo": (125, 150)
        },
        "description": "Pura energia positiva para seu momento animado! ⚡"
    },
    "cansada": {
        "genres": ["sleep", "chill", "jazz", "classical"],
        "params": {
            "valence": 0.3,
            "energy": 0.2,
            "instrumentalness": 0.7,
            "tempo": (60, 80)
        },
        "description": "Músicas suaves para relaxar e recarregar as energias 🌙"
    },
    "raivosa": {
        "genres": ["metal", "punk", "hard-rock", "industrial"],
        "params": {
            "valence": 0.2,
            "energy": 0.9,
            "loudness": -5,
            "tempo": (140, 180)
        },
        "description": "Descarga energética para liberar a tensão! 💥"
    }
}

def create_playlist_based_on_mood(mood, sp):
    mood_profile = MOOD_PROFILES.get(mood.lower(), MOOD_PROFILES["feliz"])
    user = sp.current_user()
    user_id = user["id"]
    user_name = user["display_name"]
    
    recommendations = sp.recommendations(
        seed_genres=mood_profile["genres"][:2],
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
    
    playlist_name = f"{mood.capitalize()} Vibes - {user_name}'s MoodTunes"
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=False,
        description=f"{mood_profile['description']} Gerada em {datetime.now().strftime('%d/%m/%Y')}"
    )
    
    sp.playlist_add_items(playlist["id"], track_uris)
    return playlist["external_urls"]["spotify"]