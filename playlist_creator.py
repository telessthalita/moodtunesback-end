import random

MOOD_TO_GENRES = {
    "feliz": ["pop", "dance", "indie", "reggae"],
    "triste": ["acoustic", "piano", "blues"],
    "focada": ["chill", "instrumental", "jazz"],
    "ansiosa": ["ambient", "lofi", "downtempo", "jazz"],
    "animada": ["edm", "rock", "house", "trap"],
    "cansada": ["sleep", "calm", "classical"],
    "raivosa": ["metal", "hip-hop", "punk"]
}

MOOD_PARAMETERS = {
    "feliz": {"target_valence": 0.8, "target_energy": 0.7},
    "triste": {"target_valence": 0.2, "target_energy": 0.3},
    "focada": {"target_instrumentalness": 0.7, "target_energy": 0.4},
    "ansiosa": {"target_valence": 0.3, "target_energy": 0.3, "target_instrumentalness": 0.6},
    "animada": {"target_valence": 0.9, "target_energy": 0.9},
    "cansada": {"target_valence": 0.3, "target_energy": 0.2},
    "raivosa": {"target_valence": 0.2, "target_energy": 0.8}
}


def get_mood_parameters(mood):
    return MOOD_PARAMETERS.get(mood, {"target_valence": 0.5})


def get_recommendations(sp, genres, mood_params):
    seed_genres = genres[:2] if genres else ["pop"]
    try:
        recs = sp.recommendations(seed_genres=seed_genres, limit=30, **mood_params)
        return [track["uri"] for track in recs["tracks"]]
    except Exception as e:
        print(f"[ERRO] Falha ao obter recomendações: {e}")
        return []


def create_spotify_playlist(sp, user_id, mood):
    try:
        playlist = sp.user_playlist_create(
            user=user_id,
            name=f"MoodTunes - {mood.capitalize()} Vibes",
            public=False,
            description=f"Gerado automaticamente para seu humor: {mood} 🎧"
        )
        return playlist["id"], playlist["external_urls"]["spotify"]
    except Exception as e:
        print(f"[ERRO] Falha ao criar playlist: {e}")
        return None, None


def add_tracks_to_playlist(sp, playlist_id, track_uris):
    if playlist_id and track_uris:
        try:
            sp.playlist_add_items(playlist_id, track_uris[:30])
        except Exception as e:
            print(f"[ERRO] Falha ao adicionar faixas: {e}")


def create_playlist_based_on_mood(mood, sp):
    user_id = sp.current_user()["id"]
    genres = MOOD_TO_GENRES.get(mood, ["pop"])
    mood_params = get_mood_parameters(mood)

    print(f"[INFO] Gerando recomendações para o humor '{mood}' com gêneros: {genres}")
    track_uris = get_recommendations(sp, genres, mood_params)

    if not track_uris:
        print("[AVISO] Nenhuma música encontrada para os critérios informados.")
        return None

    playlist_id, playlist_url = create_spotify_playlist(sp, user_id, mood)
    add_tracks_to_playlist(sp, playlist_id, track_uris)

    print(f"[SUCESSO] Playlist criada: {playlist_url}")
    return playlist_url
