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
    tracks = set()

    for genre in genres:
        results = sp.search(q=f"genre:{genre}", type="track", limit=15)
        for item in results["tracks"]["items"]:
            tracks.add(item["uri"])
    tracks = list(tracks)
    if len(tracks) < 5:
        additional_tracks = []
        for genre in genres:
            results = sp.search(q=f"genre:{genre}", type="track", limit=5)
            additional_tracks.extend([item["uri"] for item in results["tracks"]["items"]])
        tracks.extend(additional_tracks)

    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"MoodTunes - {mood.capitalize()} Vibes",
        public=False,
        description="Playlist gerada pela IA DJ MoodTunes 🎧"
    )

    sp.playlist_add_items(playlist["id"], tracks[:30])
    return playlist["external_urls"]["spotify"]