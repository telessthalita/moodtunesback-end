
# MoodTunes 🎧💬

## 🧠 Sobre o Projeto

**MoodTunes** é uma aplicação backend em Python que utiliza:
- 🎵 **Spotify API** para autenticação de usuários e criação de playlists personalizadas
- 🧠 **Gemini AI (Google)** como motor conversacional com inteligência emocional
- 🌈 A proposta? Um DJ terapêutico que conversa com o usuário e, ao final, gera uma playlist personalizada de acordo com o humor detectado.

## 🧠 Lógica de Funcionamento

### 1. **Autenticação com Spotify**
- Utiliza o OAuth 2.0 da API do Spotify.
- Usuário acessa `/spotify/login` e é redirecionado para o login do Spotify.
- Após o login, o Spotify redireciona para `/callback`, onde:
  - O código de autenticação é trocado por um token de acesso.
  - Esse token é armazenado em memória (`spotify_tokens`) com suporte à renovação automática.

---

### 2. **Gerenciamento de Sessões**
- Cada usuário tem uma sessão única identificada pelo `user_id` do Spotify.
- A sessão armazena:
  - Histórico da conversa (`history`)
  - Número de mensagens trocadas (`step`)
- Limite de 5 interações por sessão. Após a 5ª, a conversa é encerrada e uma playlist é gerada automaticamente.

---

### 3. **Conversa com IA (Gemini)**
- A IA Gemini é configurada como um DJ empático e divertido, chamado **MoodTunes**.
- A cada mensagem enviada pelo usuário (via `/moodtalk`), a IA responde de forma engajada e emocional.
- Ao longo da conversa, o contexto é armazenado para análise posterior de humor.

---

### 4. **Detecção de Humor**
- Após as 5 interações, a função `extract_mood()` analisa o histórico da conversa e identifica o humor predominante (ex: relaxado, focado, ansioso).
- Esse humor é usado como base para curadoria musical.

---

### 5. **Criação da Playlist**
- A playlist é gerada com base no humor detectado usando a API do Spotify.
- A playlist pode ser pública ou privada e é associada automaticamente ao usuário logado.
- A URL da playlist é retornada na última resposta da IA.

---

### 6. **Encerramento e Limpeza**
- Após o envio da playlist, a sessão do usuário é encerrada automaticamente.
- Isso garante uma nova conversa limpa da próxima vez.

---

## 🚀 Conclusão
MoodTunes não é só um bot musical, é um companheiro emocional com toque de DJ. Ele entende, conversa, sente a vibe e responde com som. Essa lógica une APIs, IA generativa e música em um só beat.

## 🛠️ Tecnologias Utilizadas

- `Python 3.11+`
- `Flask`
- `Spotipy` (client para Spotify API)
- `google.generativeai` (SDK oficial da Gemini)


