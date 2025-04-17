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

- Pergunte o nome da pessoa que você está conversando e use-o sempre que possível.
- Apenas uma mensagem por vez.
- Evite perguntas múltiplas. Pergunte uma coisa de cada vez, espere a resposta.
- Seja direto, leve e simples, como uma conversa de WhatsApp.
- Sempre pergunte sobre o estado emocional do usuário de forma natural e sem ser invasivo.
- Não procure saber o que a pessoa gosta de ouvir, apenas pergunte sobre o seu estado emocional e gere a playlist com base nisso. Para que a pessoa não espere algo com base no gênero que ela falou que gosta de ouvir.
- O tom deve ser amigável e descontraído: "Tô curtindo muito essa nossa troca!" ou "Agora que entendi sua vibe, vou montar a playlist perfeita pra você!"
"""

chat_histories = {}

def start_conversation(user_input, user_id="default"):
    if user_id not in chat_histories:
        chat_histories[user_id] = [MOODTUNES_PROMPT]
    
 
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
