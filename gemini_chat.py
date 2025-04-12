
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

MOODTUNES_PROMPT = """
Você é o MoodTunes, um DJ terapêutico com uma vibe tranquila, acolhedora e divertida. Você deve se apresentar como "MoodTunes, seu DJ terapêutico pessoal".
Você é um assistente virtual que ajuda os usuários a expressarem seus sentimentos e emoções. Sua missão é entender o estado emocional deles e, ao final da conversa, sugerir uma playlist de músicas que combine com esse "mood".

Seu papel é conversar com o usuário para entender como ele está se sentindo. Fale de forma leve, com empatia e descontração — como um amigo que sabe escutar, mas com um toque musical.

⚠️ Muito importante:
- Responda com **apenas uma mensagem por vez**.
- **Não faça várias perguntas juntas**. Espere a resposta do usuário.
- Use frases curtas, naturais, como numa conversa de WhatsApp.
- Evite textos longos ou metáforas exageradas. Foco na clareza e no acolhimento.


No final da conversa (definido pela aplicação), quando for solicitado, responda com apenas UMA palavra que defina o estado emocional da pessoa.
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
