import random

MOOD_TO_GENRES = {
    "feliz": ["pop", "dance", "indie", "reggae"],
    "triste": ["acoustic", "piano", "blues"],
    "focada": ["chill", "instrumental", "jazz"],
    "ansiosa": ["ambient", "lofi", "downtempo"],
    "animada": ["edm", "rock", "house", "trap"],
    "cansada": ["sleep", "calm", "classical"],
    "raivosa": ["metal", "hip-hop", "punk"]
}
def create_playlist_based_on_mood(mood, sp):
    user_id = sp.current_user()["id"]
    genres = MOOD_TO_GENRES.get(mood, ["pop"])
    mood_params = {
        "feliz": {"valence": 0.8, "energy": 0.7},
        "triste": {"valence": 0.2, "energy": 0.3},
        "focada": {"instrumentalness": 0.7, "energy": 0.4},
        "ansiosa": {"valence": 0.3, "energy": 0.3, "instrumentalness": 0.6},
        "animada": {"valence": 0.9, "energy": 0.9},
        "cansada": {"valence": 0.3, "energy": 0.2},
        "raivosa": {"valence": 0.2, "energy": 0.8}
    }

    recommendations = sp.recommendations(
        seed_genres=genres[:2],
        limit=30,
        **mood_params.get(mood, {})
    )

    track_uris = [track["uri"] for track in recommendations["tracks"]]

    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"MoodTunes - {mood.capitalize()} Vibes",
        public=False,
        description="Playlist gerada pela IA DJ MoodTunes 🎧"
    )

    sp.playlist_add_items(playlist["id"], track_uris)
    return playlist["external_urls"]["spotify"]