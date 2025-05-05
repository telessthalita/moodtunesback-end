import os
import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from spotify_auth import get_token_from_callback
from spotipy import Spotify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
JWT_EXPIRATION_DELTA = timedelta(days=1)

def generate_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Bem-vindo à API de autenticação do Spotify!"})

@app.route("/spotify/login", methods=["POST"])
def spotify_login():
    code = request.json.get("code")
    if not code:
        return jsonify({"error": "Faltando código de autenticação do Spotify"}), 400
    
    try:
        sp, token_info = get_token_from_callback(code)
        access_token = token_info.get("access_token")
        
        if not access_token:
            raise Exception("Token de acesso não encontrado.")
        
        sp = Spotify(auth=access_token)
        user_profile = sp.current_user()
        user_id = user_profile.get("id")
        
        if not user_id:
            raise Exception("Não foi possível obter o user_id.")

        token = generate_jwt(user_id)

        return jsonify({
            "status": "success",
            "message": "Autenticação bem-sucedida",
            "token": token
        })

    except Exception as e:
        return jsonify({
            "error": "Erro ao realizar login",
            "message": str(e)
        }), 500

@app.route("/validate_token", methods=["POST"])
def validate_token():
    token = request.json.get("token")
    if not token:
        return jsonify({"error": "Token não fornecido"}), 400

    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token['user_id']
        return jsonify({
            "status": "success",
            "user_id": user_id
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

@app.route("/moodtalk", methods=["POST"])
def mood_talk():
    data = request.get_json()
    user_id = data.get("user_id")
    user_input = data.get("message")

    if not user_id:
        return jsonify({"error": "Faltando user_id."}), 400

    return jsonify({
        "response": f"Mensagem recebida: {user_input}, para o usuário {user_id}."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
