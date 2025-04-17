import random

MOOD_TO_GENRES = {
    "feliz": ["pop", "dance"],
    "triste": ["acoustic", "piano"],
    "focada": ["instrumental", "chill"],
    "ansiosa": ["ambient", "lofi"],
    "animada": ["edm", "rock"],
    "cansada": ["sleep", "calm"],
    "raivosa": ["metal", "hip-hop"]
}

MOOD_FILTERS = {
    "feliz": {"target_valence": 0.9, "target_energy": 0.7, "target_danceability": 0.8},
    "triste": {"target_valence": 0.2, "target_acousticness": 0.8, "target_energy": 0.3},
    "focada": {"target_instrumentalness": 0.8, "target_energy": 0.4, "target_valence": 0.4},
    "ansiosa": {"target_valence": 0.3, "target_energy": 0.3, "target_acousticness": 0.6},
    "animada": {"target_valence": 0.95, "target_energy": 0.9, "target_danceability": 0.9},
    "cansada": {"target_valence": 0.2, "target_energy": 0.2, "target_acousticness": 0.7},
    "raivosa": {"target_valence": 0.2, "target_energy": 0.95, "target_loudness": -5.0}
}

def create_playlist_based_on_mood(mood, sp):
    user_id = sp.current_user()["id"]
    genres = MOOD_TO_GENRES.get(mood, ["pop"])
    
    tracks = []
    for genre in genres:
        try:
            query = f"genre:{genre}"
            results = sp.search(q=query, type="track", limit=10)
            tracks.extend([track["uri"] for track in results["tracks"]["items"]])
        except Exception as e:
            print(f"[ERRO] Falha ao buscar músicas do gênero '{genre}': {e}")

    if not tracks:
        raise Exception("Nenhuma música encontrada para os gêneros informados.")

    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"MoodTunes - {mood.capitalize()} Vibes",
        public=False,
        description=f"🎧 Playlist gerada pela IA DJ MoodTunes para um mood {mood}."
    )

    sp.playlist_add_items(playlist["id"], tracks[:30])
    return playlist["external_urls"]["spotify"]