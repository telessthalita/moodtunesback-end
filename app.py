from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from spotify_auth import get_auth_url, get_token_from_callback
from gemini_chat import start_conversation, extract_mood
from playlist_creator import create_playlist_based_on_mood
from spotipy import Spotify
import jwt
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True)

SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')  
spotify_clients = {}
user_sessions = {}

@app.route("/")
def home():
    return "🎶 Backend do MoodTunes funcionando com sucesso!"

@app.route("/spotify/login")
def spotify_login():
    try:
        auth_url = get_auth_url()
        return redirect(auth_url)
    except Exception as e:
        print(f"[ERRO] /spotify/login: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Erro ao gerar URL de autenticação com Spotify.",
            "details": str(e)
        }), 500

@app.route("/callback")
def spotify_callback():
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        return redirect("https://moodtunes.lovable.app/login?error=auth_error")

    if code:
        try:
            sp, token_info = get_token_from_callback(code)
            access_token = token_info.get("access_token")

            if not access_token:
                raise Exception("Access token ausente.")

            sp = Spotify(auth=access_token)
            user_profile = sp.current_user()
            user_id = user_profile.get("id")

            if not user_id:
                raise Exception("ID do usuário não encontrado.")

            spotify_clients[user_id] = sp

            # Em vez de fechar a janela, redireciona para a página do chat
            return redirect(f"https://moodtunes.lovable.app/chat?user_id={user_id}")

        except Exception as e:
            return redirect("https://moodtunes.lovable.app/login?error=callback_exception")
    
    return redirect("https://moodtunes.lovable.app/login?error=missing_code")
@app.route("/session_user", methods=["GET"])
def session_user():
    token = request.args.get("token")

    if not token:
        return jsonify({"error": "Token ausente"}), 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        if not user_id or user_id not in spotify_clients:
            raise Exception("Usuário não autenticado")

        return jsonify({
            "user_id": user_id,
            "status": "autenticado"
        })

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Sessão expirada"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

@app.route("/moodtalk", methods=["POST"])
def mood_talk():
    data = request.get_json()
    user_id = data.get("user_id")
    user_input = data.get("message")
    token = data.get("token")

    if not user_id or not token:
        return jsonify({"error": "Faltam dados obrigatórios (user_id ou token)."}), 400

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload.get('user_id') != user_id:
            return jsonify({"error": "Token inválido para este usuário."}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Sessão expirada"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    sp = spotify_clients.get(user_id)
    if not sp:
        return jsonify({"error": "Usuário não autenticado."}), 401

    session = user_sessions.get(user_id, {"step": 0, "history": []})
    session["history"].append(user_input)
    step = session["step"]
    session["step"] += 1
    user_sessions[user_id] = session

    if step == 7:
        try:
            mood = extract_mood(user_id)
            playlist_url = create_playlist_based_on_mood(mood, sp)
            del user_sessions[user_id]
            return jsonify({
                "resposta": (
                    f"🎵 Fechamos a vibe com chave de ouro! "
                    f"Sua playlist tá pronta: {playlist_url} "
                    f"Dá o play e curte esse som feito sob medida pra você! 🎶✨"
                ),
                "mood": mood,
                "playlist_url": playlist_url
            })
        except Exception as e:
            return jsonify({"error": f"Erro ao criar playlist: {str(e)}"}), 500

    resposta = start_conversation(user_input, user_id)
    return jsonify({
        "resposta": resposta,
        "etapa": step
    })

# Rota de resultado de mood
@app.route("/moodresult", methods=["GET"])
def mood_result():
    user_id = request.args.get("user_id", "default")
    mood = extract_mood(user_id)
    return jsonify({"mood": mood})

if __name__ == "__main__":
    app.run(debug=True, port=3000)
