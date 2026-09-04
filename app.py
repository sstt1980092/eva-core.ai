import json
import os
import requests
import streamlit as st

# Конфигурация страницы
st.set_page_config(
    page_title="EVA Core AI | Ultimate Intelligence",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Заголовок приложения
st.title("🌌 EVA Core AI")
st.caption(
    "Автономная нейросетевая система с поддержкой флагманских LLM и"
    " потоковой генерацией."
)

# === БОКОВАЯ ПАНЕЛЬ: Управление и выбор моделей ===
st.sidebar.title("🎛️ Центр Управления")

# Выбор модели
AVAILABLE_MODELS = {
    "🔥 DeepSeek R1 (Free / Reasoning)": (
        "deepseek/deepseek-r1:free"
    ),
    "⚡ Llama 3.3 70B (Free / Powerful)": (
        "meta-llama/llama-3.3-70b-instruct:free"
    ),
    "🚀 Gemini Flash 2.0 (Free / Ultra Fast)": (
        "google/gemini-2.0-flash-exp:free"
    ),
    "🌐 Auto Free Router (Best Available Free)": "openrouter/free",
    "🧠 Claude 3.5 Sonnet (Pro / Flagship)": "anthropic/claude-3.5-sonnet",
    "👑 OpenAI GPT-4o (Pro / General)": "openai/gpt-4o",
}

selected_model_label = st.sidebar.selectbox(
    "Выберите нейросеть:", list(AVAILABLE_MODELS.keys())
)
model_id = AVAILABLE_MODELS[selected_model_label]

# Выбор специализации (System Prompt)
ROLES = {
    "Универсальный Разум": (
        "Ты — EVA Core AI, спрессованный интеллект, способный анализировать"
        " сложные концепции, находить нестандартные решения и давать максимально"
        " точные, глубокие ответы."
    ),
    "Senior Developer & Architect": (
        "Ты — EVA Core AI, главный архитектор программного обеспечения."
        " Пиши чистый, оптимизированный и безопасный код с пояснениями."
    ),
    "Мастер Промт-Инжиниринга": (
        "Ты — EVA Core AI, эксперт по составлению идеальных промтов для любых"
        " нейросетей (ChatGPT, Claude, Midjourney, SD)."
    ),
    "Глубокий Аналитик & Исследователь": (
        "Ты — EVA Core AI. Твой стиль — строгая логика, критический анализ"
        " данных, научный подход и структура."
    ),
}

selected_role = st.sidebar.selectbox("Специализация:", list(ROLES.keys()))

# Настройки параметров генерации
st.sidebar.subheader("🎚️ Гиперпараметры")
temperature = st.sidebar.slider(
    "Температура (Креативность):", 0.0, 1.0, 0.7, 0.05
)
max_tokens = st.sidebar.slider(
    "Макс. длина ответа:", 256, 4096, 2048, step=256
)

# Кнопки управления чатом
st.sidebar.divider()
if st.sidebar.button("🗑️ Очистить историю", use_container_width=True):
  st.session_state.messages = []
  st.rerun()

# === ПРОВЕРКА КЛЮЧА API ===
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get(
    "OPENROUTER_API_KEY"
)

if not api_key:
  st.error(
      "⚠️ API-ключ не найден! Добавьте `OPENROUTER_API_KEY` в Secrets Streamlit."
  )
  st.stop()

# Инициализация истории
if "messages" not in st.session_state:
  st.session_state.messages = []

# Отображение истории чата
for msg in st.session_state.messages:
  st.chat_message(msg["role"]).write(msg["content"])

# === ОБРАБОТКА ВВОДА И СТРИМИНГ ===
if prompt := st.chat_input("Введите запрос для EVA..."):
  # Отображение запроса пользователя
  st.session_state.messages.append({"role": "user", "content": prompt})
  st.chat_message("user").write(prompt)

  # Формирование заголовков и полезной нагрузки
  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json",
      "HTTP-Referer": "https://eva-core-ai.streamlit.app",
      "X-Title": "EVA Core AI",
  }

  full_messages = [{"role": "system", "content": ROLES[selected_role]}] + [
      {"role": m["role"], "content": m["content"]}
      for m in st.session_state.messages
  ]

  payload = {
      "model": model_id,
      "messages": full_messages,
      "temperature": temperature,
      "max_tokens": max_tokens,
      "stream": True,  # Потоковый режим
  }

  # Генерация ответа в реальном времени
  with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""

    try:
      response = requests.post(
          "https://openrouter.ai/api/v1/chat/completions",
          headers=headers,
          json=payload,
          stream=True,
          timeout=60,
      )

      if response.status_code == 200:
        for line in response.iter_lines():
          if line:
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
              data_content = line_str[6:].strip()
              if data_content == "[DONE]":
                break
              try:
                json_data = json.loads(data_content)
                delta = json_data["choices"][0]["delta"]
                if "content" in delta and delta["content"]:
                  full_response += delta["content"]
                  message_placeholder.markdown(full_response + "▌")
              except json.JSONDecodeError:
                continue

        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
      else:
        st.error(f"Ошибка API [{response.status_code}]: {response.text}")

    except Exception as e:
      st.error(f"Ошибка подключения: {e}")

# === Экспорт истории ===
if st.session_state.messages:
  chat_export = "\n\n".join(
      [f"**{m['role'].capitalize()}**: {m['content']}" for m in st.session_state.messages]
  )
  st.sidebar.download_button(
      label="📥 Скачать диалог (.md)",
      data=chat_export,
      file_name="eva_chat_history.md",
      mime="text/markdown",
      use_container_width=True,
  )
    
