import os
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

MOOD_TO_GENRES = {
    "feliz": ["pop", "dance"],
    "triste": ["acoustic", "piano"],
    "focada": ["instrumental", "chill"],
    "ansiosa": ["ambient", "lofi"],
    "animada": ["edm", "rock"],
    "cansada": ["sleep", "calm"],
    "raivosa": ["metal", "hip-hop"],
    "nostalgico": ["pop", "rock"]
}

MOOD_FILTERS = {
    "feliz": {"target_valence": 0.9, "target_energy": 0.7, "target_danceability": 0.8},
    "triste": {"target_valence": 0.2, "target_acousticness": 0.8, "target_energy": 0.3},
    "focada": {"target_instrumentalness": 0.8, "target_energy": 0.4, "target_valence": 0.4},
    "ansiosa": {"target_valence": 0.3, "target_energy": 0.3, "target_acousticness": 0.6},
    "animada": {"target_valence": 0.95, "target_energy": 0.9, "target_danceability": 0.9},
    "cansada": {"target_valence": 0.2, "target_energy": 0.2, "target_acousticness": 0.7},
    "raivosa": {"target_valence": 0.2, "target_energy": 0.95, "target_loudness": -5.0},
    "nostalgico": {"target_valence": 0.6, "target_energy": 0.5, "target_acousticness": 0.7, "min_year": 1990, "max_year": 2010}
}

def create_playlist_based_on_mood(mood, sp):
    try:
        user_id = sp.current_user()["id"]
        mood_filters = MOOD_FILTERS.get(mood, {})
        seed_genres = MOOD_TO_GENRES.get(mood, ["pop"])
        
        try:
            recommendations = sp.recommendations(
                seed_genres=seed_genres[:5],  
                limit=30,
                **mood_filters
            )
            tracks = [track["uri"] for track in recommendations["tracks"]]
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            tracks = []
            

            for genre in seed_genres[:2]:
                try:
                    results = sp.search(q=f"genre:{genre}", type="track", limit=15)
                    tracks.extend([track["uri"] for track in results["tracks"]["items"]])
                except Exception as e:
                    print(f"Error searching genre {genre}: {str(e)}")

        if not tracks:
            raise Exception("Nenhuma música encontrada para os gêneros informados.")

        unique_artists = set()
        final_tracks = []
        
        for track in tracks:
            try:
                track_details = sp.track(track)
                artist_id = track_details["artists"][0]["id"]
                if artist_id not in unique_artists:
                    unique_artists.add(artist_id)
                    final_tracks.append(track)
                    if len(final_tracks) >= 20:
                        break
            except Exception as e:
                print(f"Error processing track {track}: {str(e)}")

        try:
            wildcard = sp.recommendations(
                seed_genres=["classical", "electronic", "jazz"],
                limit=1,
                **{k: min(0.5, v) for k, v in mood_filters.items()}
            )
            if wildcard["tracks"]:
                final_tracks.append(wildcard["tracks"][0]["uri"])
        except Exception as e:
            print(f"Error adding wildcard: {str(e)}")

        if mood == "feliz":
            final_tracks.sort(key=lambda x: sp.track(x)["popularity"], reverse=True)
        elif mood == "triste":
            final_tracks.sort(key=lambda x: sp.track(x)["duration_ms"], reverse=True)

        mood_descriptions = {
            "feliz": "☀️ Playlist solar para dias brilhantes",
            "triste": "🌧️ Canções acolhedoras para momentos introspectivos",
            "raivosa": "⚡ Energia crua para liberar a fúria",
            "nostalgico": "🕰️ Viagem no tempo através das melodias"
        }
        
        playlist = sp.user_playlist_create(
            user=user_id,
            name=f"MT • {mood.capitalize()} Vibes • {datetime.now().strftime('%d/%m')}",
            public=False,
            description=mood_descriptions.get(mood, f"🎧 Sintonia perfeita para seu mood {mood}")
        )

        if len(final_tracks) > 15:
            sp.playlist_add_items(playlist["id"], final_tracks[:15])
            sp.playlist_add_items(playlist["id"], final_tracks[15:])
        else:
            sp.playlist_add_items(playlist["id"], final_tracks)
        
        return playlist["external_urls"]["spotify"]
    
    except Exception as e:
        print(f"Error in create_playlist_based_on_mood: {str(e)}")
        raise