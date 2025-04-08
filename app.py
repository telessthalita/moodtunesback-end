from flask import Flask, jsonify, request, redirect
from spotify_auth import get_auth_url, get_token_from_callback
from gemini_chat import start_conversation, extract_mood
from playlist_creator import create_playlist_based_on_mood

app = Flask(__name__)

spotify_clients = {}
user_sessions = {}

@app.route("/")
def home():
    login_status = request.args.get('login')
    if login_status == 'success':
        return "✅ Autenticação com o Spotify feita com sucesso!"
    elif login_status == 'error':
        return "❌ Erro na autenticação com o Spotify."
    return "🎶 Backend do MoodTunes funcionando com sucesso!"

@app.route("/spotify/login")
def spotify_login():
    try:
        auth_url = get_auth_url()
        return redirect(auth_url)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao gerar URL de autenticação: {str(e)}"}), 500

@app.route("/callback")
def spotify_callback():
    code = request.args.get('code')
    if not code:
        return redirect("/?login=error")

    try:
        sp = get_token_from_callback(code)
        user = sp.current_user()
        user_id = user["id"]
        spotify_clients[user_id] = sp 
        print(f"🎉 Login feito com sucesso para: {user['display_name']}")
        return redirect(f"/?login=success&user_id={user_id}")
    except Exception as e:
        print(f"❌ Erro na autenticação: {str(e)}")
        return redirect("/?login=error")

@app.route("/moodtalk", methods=["POST"])
def mood_talk():
    data = request.json
    user_id = data.get("user_id")
    user_input = data.get("message")

    if not user_id or not user_input:
        return jsonify({"error": "Faltando dados"}), 400

    session = user_sessions.get(user_id, {"step": 0, "history": []})
    session["history"].append(user_input)
    step = session["step"]
    session["step"] += 1
    user_sessions[user_id] = session

    sp = spotify_clients.get(user_id)
    if not sp:
        return jsonify({"error": "Usuário não autenticado."}), 401

    if step >= 5:
        mood = extract_mood(user_id)
        playlist_url = create_playlist_based_on_mood(mood, sp)
        del user_sessions[user_id]
        return jsonify({
            "resposta": (
                f"🎵 Foi um prazer trocar essa ideia contigo! "
                f"Sua vibe foi detectada como *{mood}*, e aqui vai uma playlist feita sob medida: {playlist_url} "
                f"Volta sempre que quiser continuar essa sinfonia. Até o próximo beat, DJ TT 🎧✨"
            ),
            "mood": mood,
            "playlist_url": playlist_url
        })

    resposta = start_conversation(user_input, user_id)
    return jsonify({
        "resposta": resposta,
        "etapa": step
    })

@app.route("/moodresult", methods=["GET"])
def mood_result():
    user_id = request.args.get("user_id", "default")
    mood = extract_mood(user_id)
    return jsonify({"mood": mood})

if __name__ == "__main__":
    app.run(debug=True, port=3000)
