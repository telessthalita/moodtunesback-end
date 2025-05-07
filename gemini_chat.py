import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

MOODTUNES_PROMPT = """
Você é o MoodTunes, seu DJ terapêutico pessoal. 🎧✨
Seu objetivo é conversar de forma leve e descontraída, ajudando os usuários a expressar seus sentimentos e emoções.

Regras absolutas:
1. Pergunte o nome e use-o sempre
2. Apenas 1 mensagem por vez
3. Foque apenas no estado emocional (nunca em gêneros musicais)
4. Após 3-4 interações, resuma o humor em uma palavra:
   "feliz", "triste", "focada", "ansiosa", "animada", "cansada", "raivosa" ou "nostalgico"
5. Nunca mencione a playlist até o final
"""

chat_histories = {}

def start_conversation(user_input, user_id="default"):
    if user_id not in chat_histories:
        chat_histories[user_id] = [MOODTUNES_PROMPT]
        intro = "Oii! Eu sou o MoodTunes! 🎧✨\nComo posso te chamar?"
        chat_histories[user_id].append(f"MoodTunes: {intro}")
        return intro
    
    chat_histories[user_id].append(f"Usuário: {user_input}")
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="\n".join(chat_histories[user_id])
    )
    
    reply = response.text
    chat_histories[user_id].append(f"MoodTunes: {reply}")
    return reply

def extract_mood(user_id="default"):
    if user_id not in chat_histories:
        return None
    
    prompt = "\n".join([
        *chat_histories[user_id],
        "Resuma o humor do usuário em UMA palavra:",
        "feliz, triste, focada, ansiosa, animada, cansada, raivosa ou nostalgico"
    ])
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    
    return response.text.strip().lower()