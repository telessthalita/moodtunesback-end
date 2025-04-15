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
    
    GENRE_SEARCH_TERMS = {
        "pop": "tag:new pop",
        "indie": "tag:indie year:2020-2023",
        "dance": "tag:dance",
        "reggae": "genre:reggae",
        "acoustic": "tag:acoustic",
        "piano": "piano",
        "blues": "genre:blues",
        "chill": "tag:chill",
        "instrumental": "tag:instrumental",
        "jazz": "genre:jazz",
        "ambient": "tag:ambient",
        "lofi": "tag:lofi",
        "downtempo": "tag:downtempo",
        "edm": "tag:edm",
        "rock": "tag:indie rock",
        "house": "tag:house",
        "trap": "tag:trap",
        "sleep": "tag:sleep",
        "calm": "tag:calm",
        "classical": "genre:classical",
        "metal": "tag:metal",
        "hip-hop": "tag:hiphop",
        "punk": "tag:punk"
    }
    
    tracks = set()
    
    for genre in genres:
        search_query = GENRE_SEARCH_TERMS.get(genre, f"tag:{genre}")
        try:
            playlist_results = sp.search(q=search_query, type='playlist', limit=2)
            if playlist_results['playlists']['items']:
                playlist_tracks = sp.playlist_tracks(playlist_results['playlists']['items'][0]['id'])
                tracks.update(item['track']['uri'] for item in playlist_tracks['items'] if item['track'])
            
            track_results = sp.search(q=search_query, type='track', limit=15)
            tracks.update(item['uri'] for item in track_results['tracks']['items'])
            
        except Exception as e:
            continue

    tracks = list(tracks)
    
    if len(tracks) < 10:
        try:
            recommendations = sp.recommendations(
                seed_genres=genres[:2],
                limit=20,
                market="BR"
            )
            tracks.extend([track['uri'] for track in recommendations['tracks']])
        except Exception as e:
            pass

    tracks = list(set(tracks))
    
    if not tracks:
        recommendations = sp.recommendations(seed_genres=["pop"], limit=30)
        tracks = [track['uri'] for track in recommendations['tracks']]

    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"MoodTunes - {mood.capitalize()} Vibes",
        public=False,
        description="Playlist gerada pela IA DJ MoodTunes 🎧"
    )

    for i in range(0, len(tracks), 100):
        sp.playlist_add_items(playlist["id"], tracks[i:i+100])

    return playlist["external_urls"]["spotify"]