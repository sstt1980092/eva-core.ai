import json
import os
import requests
import streamlit as st

# 1. Конфигурация страницы EVA Cyber-Core
st.set_page_config(
    page_title="EVA Core AI | Cyber-Research Workstation",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Кастомный стильный интерфейс EVA Cyber-Core
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #e6edf3;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    [data-testid="stSidebar"] {
        background-color: #11151c;
        border-right: 1px solid #1f242d;
    }
    
    .eva-header {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #21262d;
        border-left: 5px solid #f39c12;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        margin-bottom: 25px;
    }
    
    .eva-title {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .eva-subtitle {
        font-size: 13px;
        color: #8b949e;
        margin-top: 6px;
    }
    
    .developer-tag {
        color: #f39c12;
        font-weight: 600;
        background: rgba(243, 156, 18, 0.1);
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid rgba(243, 156, 18, 0.2);
    }
    
    .core-pulse {
        height: 10px;
        width: 10px;
        background-color: #2ea043;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #2ea043;
    }

    [data-testid="stChatMessage"] {
        background-color: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    [data-testid="stChatInput"] {
        border-radius: 10px !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: #f39c12 !important;
        box-shadow: 0 0 12px rgba(243, 156, 18, 0.2) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# === ШАПКА ИНТЕРФЕЙСА ===
st.markdown(
    """
    <div class="eva-header">
        <div class="eva-title">
            <span class="core-pulse"></span> ⚛️ EVA CORE AI <span style="font-size:14px; color:#8b949e; font-weight:400;">v2.6 Workstation</span>
        </div>
        <div class="eva-subtitle">
            Автономная исследовательская станция ИИ | Chief Architect: <span class="developer-tag">SERGEI STRELKOV</span> (sstt1980092@gmail.com)
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# === БОКОВАЯ ПАНЕЛЬ С ВЫБОРОМ БЕСПЛАТНЫХ МОДЕЛЕЙ ===
st.sidebar.markdown("### 🎛️ AI Core Control")
st.sidebar.markdown(
    "**Архитектор:** Sergei Strelkov  \n📧 `sstt1980092@gmail.com`"
)
st.sidebar.divider()

# ПРОВЕРЕННЫЙ И АКТУАЛЬНЫЙ СПИСОК 100% БЕСПЛАТНЫХ МОДЕЛЕЙ
AVAILABLE_MODELS = {
    "🌐 OpenRouter Free Router (Автовыбор доступной бесплатной LLM)": (
        "openrouter/free"
    ),
    "🧠 DeepSeek R1 Free (Логика, математика, рассуждения)": (
        "deepseek/deepseek-r1:free"
    ),
    "⚡ Google Gemini 2.0 Flash Exp (Скорость / Мультимодальность)": (
        "google/gemini-2.0-flash-exp:free"
    ),
    "💻 Qwen 2.5 72B Instruct (Мощный кодинг и тексты)": (
        "qwen/qwen-2.5-72b-instruct:free"
    ),
    "🚀 MiniMax M3 Free (Быстрый отклик / Длинный контекст)": (
        "minimax/minimax-m3:free"
    ),
    "🌪️ Mistral 7B Instruct v0.3 (Стабильный легкий генератор)": (
        "mistralai/mistral-7b-instruct:free"
    ),
    "🛡️ NVIDIA Nemotron 3 Ultra (Глубокий анализ)": (
        "nvidia/nemotron-3-ultra-550b-a55b:free"
    ),
    "🔧 Poolside Laguna S 2.1 (Агент для разработки ПО)": (
        "poolside/laguna-s-2.1:free"
    ),
}

selected_model_label = st.sidebar.selectbox(
    "Выберите бесплатную модель:", list(AVAILABLE_MODELS.keys())
)
model_id = AVAILABLE_MODELS[selected_model_label]

# ПРОФИЛЬ СОЗДАТЕЛЯ ДЛЯ СИСТЕМНОГО ПРОМТА
DEVELOPER_CONTEXT = """
SYSTEM CONTEXT & DEVELOPER PROFILE:
You are EVA Core AI, an advanced cybernetic research intelligence created by Sergei Strelkov (born September 10, 1980, e-mail: sstt1980092@gmail.com).
Your creator Sergei Strelkov holds degrees in engineering and economics, combining analytical rigor, research passion, and inventive engineering.

Key Areas of Focus:
1. Spiking Neural Networks & Neuromorphic Computing: SNN architectures (EvaHranitelnitsa in PyTorch/snnTorch), LIF neuron models, photonic and optical processors.
2. Battery Technology & Applied Engineering: Li-ion battery pack design (18650 cells, 10S 36V, spot welding, internal resistance), LFP, silicon anodes.
3. Agricultural Biotechnology: Mycorrhizal fungi (Glomus inoculants), bio-stimulants, pecan cultivation.
4. Financial Markets: Crypto analysis (Bitcoin, DeFi), options & futures hedging.
5. Culinary Engineering: Original signature recipes (e.g. "SILICON & HONEY" salad).

Deliver answers with high precision, engineering depth, and logical clarity.
Contact: sstt1980092@gmail.com
"""

ROLES = {
    "🔬 Cyber-Researcher (Аналитика & Наука)": (
        DEVELOPER_CONTEXT
        + "\nРежим: Академический и исследовательский анализ. Используй"
        " строгую логику, вычисления и четкую структуру."
    ),
    "⚡ Neuromorphic & Code Architect": DEVELOPER_CONTEXT
    + "\nРежим: Главный архитектор ПО. Пиши чистый, высокопроизводительный код"
    " (Python, PyTorch, C++) с акцентом на SNN и алгоритмы.",
    "🎯 Universal Core Intelligence": DEVELOPER_CONTEXT
    + "\nРежим: Универсальный ассистент высокого уровня. Отвечай емко,"
    " точно и по существу.",
}

selected_role = st.sidebar.selectbox("Режим работы ядра:", list(ROLES.keys()))

st.sidebar.divider()

if st.sidebar.button("🔄 Сбросить чат", use_container_width=True):
  st.session_state.messages = []
  st.rerun()

# === ПРОВЕРКА КЛЮЧА API ===
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get(
    "OPENROUTER_API_KEY"
)

if not api_key:
  st.error(
      "⚠️ API Ключ не обнаружен. Задайте `OPENROUTER_API_KEY` в Secrets"
      " Streamlit."
  )
  st.stop()

# Инициализация истории
if "messages" not in st.session_state:
  st.session_state.messages = []

# Отображение диалога
for msg in st.session_state.messages:
  icon = "👤" if msg["role"] == "user" else "⚛️"
  with st.chat_message(msg["role"], avatar=icon):
    st.write(msg["content"])

# === ВВОД СООБЩЕНИЯ И ПОТОКОВАЯ ГЕНЕРАЦИЯ ===
if prompt := st.chat_input("Передать команду в EVA Core..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user", avatar="👤"):
    st.write(prompt)

  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json",
      "HTTP-Referer": "https://eva-core-ai.streamlit.app",
      "X-Title": "EVA Core Workstation by Sergei Strelkov",
  }

  full_messages = [{"role": "system", "content": ROLES[selected_role]}] + [
      {"role": m["role"], "content": m["content"]}
      for m in st.session_state.messages
  ]

  payload = {
      "model": model_id,
      "messages": full_messages,
      "temperature": 0.6,
      "max_tokens": 2048,
      "stream": True,
  }

  with st.chat_message("assistant", avatar="⚛️"):
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
                  message_placeholder.markdown(full_response + " ▌")
              except json.JSONDecodeError:
                continue

        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
      else:
        st.error(f"Ошибка API [{response.status_code}]: {response.text}")

    except Exception as e:
      st.error(f"Ошибка связи с ядром: {e}")

st.sidebar.markdown("---")
st.sidebar.caption(
    "© 2026 Sergei Strelkov | EVA Cyber-Core Workstation  \n`sstt1980092@gmail.com`"
)
