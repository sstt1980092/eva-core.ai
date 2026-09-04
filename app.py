import os
import requests
import streamlit as st

st.set_page_config(page_title="EVA Core AI", page_icon="🤖")
st.title("🤖 EVA Core AI")

# Получение API-ключа из Secrets Streamlit или переменных окружения
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get(
    "OPENROUTER_API_KEY"
)

if not api_key:
  st.warning("⚠️ Пожалуйста, укажите OPENROUTER_API_KEY в Secrets Streamlit.")
  st.stop()

if "messages" not in st.session_state:
  st.session_state.messages = []

for msg in st.session_state.messages:
  st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Задайте вопрос..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  st.chat_message("user").write(prompt)

  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json",
  }

  payload = {
      "model": "google/gemma-2-9b-it:free",
      "messages": st.session_state.messages,
  }

  with st.spinner("EVA думает..."):
    try:
      response = requests.post(
          "https://openrouter.ai/api/v1/chat/completions",
          headers=headers,
          json=payload,
      )

      if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        st.chat_message("assistant").write(answer)
      else:
        st.error(f"Ошибка API: {response.status_code} - {response.text}")
    except Exception as e:
      st.error(f"Ошибка соединения: {e}")
