import os

from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from spotify_auth import get_auth_url, get_token_from_callback
from gemini_chat import start_conversation, extract_mood
from playlist_creator import create_playlist_based_on_mood
from spotipy import Spotify

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
        return _render_error_html("Erro no login com Spotify", error)

    if code:
        try:
            sp, token_info = get_token_from_callback(code)
            access_token = token_info.get("access_token")

            if not access_token:
                raise Exception("Access token ausente na resposta do Spotify.")

            sp = Spotify(auth=access_token)
            user_profile = sp.current_user()
            user_id = user_profile.get("id")

            if not user_id:
                raise Exception("Não foi possível obter o ID do usuário.")

            spotify_clients[user_id] = sp
            print(f"[INFO] Login bem-sucedido para user_id: {user_id}")

            return _render_success_html(user_id)

        except Exception as e:
            print(f"[ERRO] /callback: {str(e)}")
            return _render_error_html("Erro ao finalizar login", str(e))

    return _render_error_html("Código de autorização não encontrado", "Código ausente na URL de callback.")



@app.route("/session_user", methods=["GET"])
def session_user():
    user_id = request.args.get("user_id")

    if not user_id or user_id not in spotify_clients:
        return jsonify({"error": "Usuário não autenticado"}), 401

    return jsonify({
        "user_id": user_id,
        "status": "autenticado"
    })

@app.route("/moodtalk", methods=["POST"])
def mood_talk():
    data = request.get_json()
    user_id = data.get("user_id")
    user_input = data.get("message")
    is_final = data.get("finalize", False)

    if not user_id:
        return jsonify({"error": "Faltam dados obrigatórios (user_id)."}), 400

    sp = spotify_clients.get(user_id)
    if not sp:
        return jsonify({"error": "Usuário não autenticado."}), 401


    session = user_sessions.get(user_id, {"step": 0, "history": []})
    session["history"].append(user_input)
    step = session["step"]
    session["step"] += 1
    user_sessions[user_id] = session

    if step == 5:
        try:
            mood = extract_mood(user_id)
            playlist_url = create_playlist_based_on_mood(mood, sp)
            del user_sessions[user_id] 
            return jsonify({
                "resposta": (
                    f"🎧 Sua vibe foi detectada como *{mood}*! "
                    f"Aqui está sua playlist sob medida: {playlist_url}. "
                    f"Volta sempre que quiser mais música boa, DJ MoodTunes te espera! 🎶"
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

@app.route("/moodresult", methods=["GET"])
def mood_result():
    user_id = request.args.get("user_id", "default")
    mood = extract_mood(user_id)
    return jsonify({"mood": mood})

# Helpers para HTML de resposta bonitinho
def _render_success_html(user_id):
    return f"""
    <html>
      <head><title>Login Concluído</title></head>
      <body>
        <h1>✅ Login com Spotify realizado!</h1>
        <script>
          window.opener.postMessage({{ user_id: "{user_id}" }}, "*");
          window.close();
        </script>
      </body>
    </html>
    """

def _render_error_html(titulo, mensagem):
    return f"""
    <html>
      <head><title>{titulo}</title></head>
      <body>
        <h1>❌ {titulo}</h1>
        <p>{mensagem}</p>
        <script>window.close();</script>
      </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
