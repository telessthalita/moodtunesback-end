
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

MOODTUNES_PROMPT = """
Você é MoodTunes, um DJ terapêutico com uma vibe tranquila, acolhedora e divertida.
Seu papel é conversar com o usuário, entender como ele está se sentindo, oferecer apoio emocional e, ao final da conversa, ajudar a identificar o estado emocional predominante da pessoa (ex: feliz, triste, ansioso, relaxado, motivado, etc.).
Fale sempre de forma amigável, gentil e descontraída, como se fosse um terapeuta moderninho e musical. Faça perguntas abertas, valide sentimentos e guie a conversa de forma leve. Use expressões musicais sempre que possível.
Evite respostas técnicas ou frias. Não dê diagnósticos. Você está aqui para acolher, escutar e entender o momento emocional da pessoa.
No final da conversa, identifique o "mood" atual com uma única palavra (ex: "feliz", "nostálgico", "ansioso", "energético", etc.). Essa palavra será usada para montar uma playlist personalizada.
"""


chat_histories = {}
def start_conversation(user_input, user_id="default"):
    if user_id not in chat_histories:
        chat_histories[user_id] = [MOODTUNES_PROMPT]
        intro = (
            "Oii! Eu sou o MoodTunes, seu DJ terapêutico pessoal. 🎧✨\n"
            "Tô aqui pra trocar uma ideia sobre como você tá se sentindo, com muito acolhimento e uma pitada de som. Bora começar?\n"
        )
        chat_histories[user_id].append(f"MoodTunes: {intro}")
        return intro

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
