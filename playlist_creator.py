def fits_mood(features, mood):
    if not features:
        return False

    valence = features["valence"]
    energy = features["energy"]
    danceability = features["danceability"]
    acousticness = features["acousticness"]

    mood_rules = {
        "feliz": valence > 0.6 and danceability > 0.5,
        "triste": valence < 0.4 and acousticness > 0.5,
        "raivosa": energy > 0.7 and valence < 0.5,
        "focada": acousticness > 0.3 and energy < 0.7,
        "cansada": valence < 0.5 and energy < 0.5,
        "ansiosa": acousticness > 0.4 and danceability < 0.6,
        "nostalgico": acousticness > 0.4 and valence < 0.5,
        "animada": energy > 0.6 and danceability > 0.6
    }

    return mood_rules.get(mood, lambda: True)

def create_playlist_based_on_mood(mood, sp):
    try:
        user_id = sp.current_user()["id"]
        mood_filters = MOOD_FILTERS.get(mood, {})
        seed_genres = MOOD_TO_GENRES.get(mood, ["pop"])
        unique_track_ids = set()
        unique_artist_ids = set()
        final_tracks = []

        try:
            recommendations = sp.recommendations(
                seed_genres=seed_genres[:5],
                limit=25,
                **mood_filters
            )
            tracks = [track["uri"] for track in recommendations["tracks"]]
        except:
            tracks = []
            for genre in seed_genres[:2]:
                try:
                    results = sp.search(q=f"genre:{genre}", type="track", limit=20)
                    tracks.extend([track["uri"] for track in results["tracks"]["items"]])
                except:
                    pass

        random.shuffle(tracks)

        for track in tracks:
            try:
                if track in unique_track_ids:
                    continue
                track_details = sp.track(track)
                artist_id = track_details["artists"][0]["id"]
                features = sp.audio_features(track)[0]
                if fits_mood(features, mood) and artist_id not in unique_artist_ids:
                    unique_track_ids.add(track)
                    unique_artist_ids.add(artist_id)
                    final_tracks.append(track)
                if len(final_tracks) >= 10:
                    break
            except:
                continue

        if len(final_tracks) < 10:
            wildcard_genres = random.sample(["classical", "electronic", "jazz", "world", "experimental"], 2)
            try:
                wildcard = sp.recommendations(
                    seed_genres=wildcard_genres,
                    limit=5,
                    **{k: v * 0.7 for k, v in mood_filters.items()}
                )
                for track in wildcard["tracks"]:
                    uri = track["uri"]
                    artist_id = track["artists"][0]["id"]
                    features = sp.audio_features([uri])[0]
                    if uri not in unique_track_ids and artist_id not in unique_artist_ids and fits_mood(features, mood):
                        unique_track_ids.add(uri)
                        unique_artist_ids.add(artist_id)
                        final_tracks.append(uri)
            except:
                pass

        if mood == "feliz":
            final_tracks.sort(key=lambda x: (
                sp.track(x)["popularity"],
                sp.audio_features(x)[0]["danceability"]
            ), reverse=True)
        elif mood == "triste":
            final_tracks.sort(key=lambda x: (
                sp.audio_features(x)[0]["acousticness"],
                sp.track(x)["duration_ms"]
            ), reverse=True)
        elif mood == "raivosa":
            final_tracks.sort(key=lambda x: sp.audio_features(x)[0]["energy"], reverse=True)
        else:
            random.shuffle(final_tracks)

        mood_emojis = {
            "feliz": "☀️", "triste": "🌧️", "focada": "📚", 
            "ansiosa": "🌀", "animada": "⚡", "cansada": "😴",
            "raivosa": "🔥", "nostalgico": "🕰️"
        }

        mood_descriptions = {
            "feliz": f"{mood_emojis.get(mood, '🎵')} Playlist para elevar seu astral",
            "triste": f"{mood_emojis.get(mood, '🎵')} Melodias para momentos introspectivos",
            "focada": f"{mood_emojis.get(mood, '🎵')} Concentração máxima com essas faixas",
            "ansiosa": f"{mood_emojis.get(mood, '🎵')} Acalmando a mente com sons suaves",
            "animada": f"{mood_emojis.get(mood, '🎵')} Energia pura para seu dia",
            "cansada": f"{mood_emojis.get(mood, '🎵')} Descanso musical para relaxar",
            "raivosa": f"{mood_emojis.get(mood, '🎵')} Libere sua energia com essas batidas",
            "nostalgico": f"{mood_emojis.get(mood, '🎵')} Uma viagem no tempo musical"
        }

        playlist = sp.user_playlist_create(
            user=user_id,
            name=f"MoodTunes {mood_emojis.get(mood, '🎵')} {mood.capitalize()} • {datetime.now().strftime('%d/%m')}",
            public=False,
            description=mood_descriptions.get(mood, f"Sintonia perfeita para seu mood {mood}")
        )

        sp.playlist_add_items(playlist["id"], final_tracks[:100])
        return playlist["external_urls"]["spotify"]

    except Exception as e:
        print(f"Error in create_playlist_based_on_mood: {str(e)}")
        raise
