import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

MOODTUNES_PROMPT = """
Você é o MoodTunes, seu DJ terapêutico pessoal. 🎧✨
Seu objetivo é conversar de forma leve e descontraída, ajudando os usuários a expressar seus sentimentos e emoções. No final da conversa, você criará uma playlist com base no "mood" do usuário.

Fale com empatia, como um amigo que sabe escutar, mas sempre com um toque musical. Evite textos longos ou metáforas complicadas. Seja direto e acolhedor, sem perder o ritmo da conversa!

Regras importantes:
Pergunte o nome de quem você está conversando 

Apenas uma mensagem por vez.

Evite perguntas múltiplas. Pergunte uma coisa de cada vez, espere a resposta.

Seja direto, leve e simples, como uma conversa de WhatsApp.

Sempre pergunte sobre o estado emocional do usuário de forma natural e sem ser invasivo.

Se você perguntar do gosto musical do usuario, ou ele der uma opção de genero, leve em consideração na hora de montar a playlist.

O tom deve ser amigável e descontraído: "Tô curtindo muito essa nossa troca!" ou "Agora que entendi sua vibe, vou montar a playlist perfeita pra você!"
"""

chat_histories = {}

def start_conversation(user_input, user_id="default"):
    if user_id not in chat_histories:
        chat_histories[user_id] = [MOODTUNES_PROMPT]
        intro = "Oii! Eu sou o MoodTunes, seu DJ terapêutico pessoal. 🎧✨ Tô aqui pra trocar uma ideia sobre como você tá se sentindo. Vamos começar?"
        chat_histories[user_id].append(f"MoodTunes: {intro}")
        return intro

    # Coletando o nome do usuário de maneira natural
    if "nome" not in chat_histories[user_id]:
        user_name = user_input.strip()
        chat_histories[user_id].append(f"Usuário: {user_name}")
        return f"Legal, {user_name}! Agora, me conta, como você tá se sentindo hoje?"

    chat_histories[user_id].append(f"Usuário: {user_input}")
    full_context = "\n".join(chat_histories[user_id])
    full_context += "\nMoodTunes: Lembre-se: responda com no máximo 3 parágrafos curtos, de forma leve e musical."

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=full_context
    )

    reply = response.text
    chat_histories[user_id].append(f"MoodTunes: {reply}")
    return reply


def extract_mood_and_genre(user_id="default"):
    if user_id not in chat_histories:
        return {"mood": "desconhecido", "genre": None}

    full_context = "\n".join(chat_histories[user_id])
    full_context += "\nMoodTunes: Agora diga apenas:\nMood: <estado emocional>\nGênero: <gênero musical ou None>"

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=full_context
    )

    lines = response.text.lower().strip().splitlines()
    result = {"mood": "desconhecido", "genre": None}

    for line in lines:
        if "mood:" in line:
            result["mood"] = line.replace("mood:", "").strip()
        if "gênero:" in line:
            result["genre"] = line.replace("gênero:", "").strip() or None

    return result

def extract_mood(user_id="default"):
    if user_id not in chat_histories:
        return "sem conversa"

    full_context = "\n".join(chat_histories[user_id])
    full_context += "\nMoodTunes: Agora diga apenas uma palavra que representa o estado emocional do usuário."

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=full_context
    )

    return response.text.strip().lower()

def reset_user_context(user_id="default"):
    if user_id in chat_histories:
        prompt_base = chat_histories[user_id][0]
        chat_histories[user_id] = [prompt_base]
