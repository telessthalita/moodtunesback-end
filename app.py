from flask import Flask, jsonify, request, redirect, make_response
from spotify_auth import get_auth_url, get_token_from_callback
from gemini_chat import start_conversation, extract_mood
from playlist_creator import create_playlist_based_on_mood
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

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
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        return """
        <html>
          <body>
            <h1>❌ Erro no login com Spotify</h1>
            <p>Erro: {}</p>
            <script>window.close();</script>
          </body>
        </html>
        """.format(error)

    if code:
        try:
            token_info = get_token_from_callback(code)
            sp, token_info = get_valid_spotify_client(token_info)
            user_profile = sp.current_user()
            user_id = user_profile["id"]

            print(f"[INFO] Login bem-sucedido para user_id: {user_id}")

            return f"""
            <html>
              <head><title>Login Concluído</title></head>
              <body>
                <h1>✅ Login com Spotify realizado!</h1>
                <p>Usuário: {user_id}</p>
                <p>Você pode fechar esta aba agora.</p>
                <script>window.close();</script>
              </body>
            </html>
            """
        except Exception as e:
            print(f"[ERRO] Callback Spotify: {str(e)}")
            return f"""
            <html>
              <body>
                <h1>❌ Erro ao finalizar login</h1>
                <p>{str(e)}</p>
                <script>window.close();</script>
              </body>
            </html>
            """
    return """
    <html>
      <body>
        <h1>❌ Código de autorização não encontrado.</h1>
        <script>window.close();</script>
      </body>
    </html>
    """

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
@app.route("/session_user", methods=["GET"])
def session_user():
    user_id = request.args.get("user_id")

    if not user_id or user_id not in spotify_clients:
        return jsonify({"error": "Usuário não autenticado"}), 401

    return jsonify({
        "user_id": user_id,
        "status": "autenticado"
    })


@app.route("/moodresult", methods=["GET"])
def mood_result():
    user_id = request.args.get("user_id", "default")
    mood = extract_mood(user_id)
    return jsonify({"mood": mood})

if __name__ == "__main__":
    app.run(debug=True, port=3000)
