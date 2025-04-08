import random

MOOD_TO_GENRES = {
    "feliz": ["pop", "dance"],
    "triste": ["acoustic", "piano"],
    "focada": ["chill", "instrumental"],
    "ansiosa": ["ambient", "lofi"],
    "animada": ["edm", "rock"],
    "cansada": ["sleep", "calm"],
    "raivosa": ["metal", "hip-hop"]
}

def create_playlist_based_on_mood(mood, sp):
    user_id = sp.current_user()["id"]
    genres = MOOD_TO_GENRES.get(mood, ["pop"])

    tracks = []
    for genre in genres:
        results = sp.search(q=f"genre:{genre}", type="track", limit=5)
        tracks.extend([item["uri"] for item in results["tracks"]["items"]])

    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"MoodTunes - {mood.capitalize()} Vibes",
        public=False,
        description="Playlist gerada pela IA DJ MoodTunes 🎧"
    )

    sp.playlist_add_items(playlist["id"], tracks)
    return playlist["external_urls"]["spotify"]
