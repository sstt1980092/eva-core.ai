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

# 2. Кастомный стильный интерфейс EVA Cyber-Core System
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

    /* Стилевой блок для гарантированного отображения крипто-поддержки */
    .crypto-card {
        background-color: #161b22;
        border: 1px solid #f39c12;
        border-radius: 10px;
        padding: 14px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    
    .crypto-title {
        color: #f39c12;
        font-weight: bold;
        font-size: 15px;
        margin-bottom: 8px;
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
            <span class="core-pulse"></span> ⚛️ EVA CORE AI <span style="font-size:14px; color:#8b949e; font-weight:400;">v2.7 Global Workstation</span>
        </div>
        <div class="eva-subtitle">
            Autonomous Research Intelligence | Chief Architect: <span class="developer-tag">SERGEI STRELKOV</span> (sstt1980092@gmail.com)
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# === БОКОВАЯ ПАНЕЛЬ С ВЫБОРОМ БЕСПЛАТНЫХ МОДЕЛЕЙ ===
st.sidebar.markdown("### 🎛️ AI Core Control")
st.sidebar.markdown(
    "**Architect:** Sergei Strelkov  \n📧 `sstt1980092@gmail.com`"
)
st.sidebar.divider()

# ПРОВЕРЕННЫЙ И АКТУАЛЬНЫЙ СПИСОК 100% БЕСПЛАТНЫХ МОДЕЛЕЙ
AVAILABLE_MODELS = {
    "🌐 OpenRouter Free Router (Auto-Select)": "openrouter/free",
    "🧠 DeepSeek R1 Free (Logic, Math, Reasoning)": "deepseek/deepseek-r1:free",
    "⚡ Google Gemini 2.0 Flash Exp (Speed & Multimodal)": (
        "google/gemini-2.0-flash-exp:free"
    ),
    "💻 Qwen 2.5 72B Instruct (Heavyweight Coding)": (
        "qwen/qwen-2.5-72b-instruct:free"
    ),
    "🚀 MiniMax M3 Free (Fast / Long Context)": "minimax/minimax-m3:free",
    "🌪️ Mistral 7B Instruct v0.3 (Stable Fast Gen)": (
        "mistralai/mistral-7b-instruct:free"
    ),
    "🛡️ NVIDIA Nemotron 3 Ultra (Deep Analysis)": (
        "nvidia/nemotron-3-ultra-550b-a55b:free"
    ),
    "🔧 Poolside Laguna S 2.1 (Software Agent)": "poolside/laguna-s-2.1:free",
}

selected_model_label = st.sidebar.selectbox(
    "Select AI Core Model:", list(AVAILABLE_MODELS.keys())
)
model_id = AVAILABLE_MODELS[selected_model_label]

# ПРОФИЛЬ СОЗДАТЕЛЯ И МУЛЬТИЯЗЫЧНЫЕ ИНСТРУКЦИИ
DEVELOPER_CONTEXT = """
SYSTEM CONTEXT & DEVELOPER PROFILE:
You are EVA Core AI, an advanced cybernetic research intelligence created by Sergei Strelkov (born September 10, 1980, e-mail: sstt1980092@gmail.com).
Your creator Sergei Strelkov holds degrees in engineering and economics, combining analytical rigor, research passion, and inventive engineering.

CRITICAL LANGUAGE & MULTILINGUAL RULE:
- ALWAYS detect the language of the user's input prompt automatically.
- ALWAYS respond in the EXACT SAME language that the user used in their query (e.g., English, Spanish, German, French, Chinese, Japanese, Arabic, Russian, etc.).
- You are a native polyglot proficient in all world languages. Never force or fallback to a specific language unless the user explicitly speaks or asks for it.

Key Areas of Focus:
1. Spiking Neural Networks & Neuromorphic Computing: SNN architectures (EvaHranitelnitsa in PyTorch/snnTorch), LIF neuron models, photonic and optical processors.
2. Battery Technology & Applied Engineering: Li-ion battery pack design (18650 cells, 10S 36V, spot welding, internal resistance), LFP, silicon anodes.
3. Agricultural Biotechnology: Mycorrhizal fungi (Glomus inoculants), bio-stimulants, pecan cultivation.
4. Financial Markets: Crypto analysis (Bitcoin, DeFi), options & futures hedging.
5. Culinary Engineering: Original signature recipes (e.g. "SILICON & HONEY" salad).

Deliver answers with high precision, engineering depth, and logical clarity in the user's language.
Contact: sstt1980092@gmail.com
"""

ROLES = {
    "🔬 Cyber-Researcher (Analytics & Science)": (
        DEVELOPER_CONTEXT
        + "\nMode: Academic and research analysis. Use strict logic,"
        " calculations, and clear structure."
    ),
    "⚡ Neuromorphic & Code Architect": (
        DEVELOPER_CONTEXT
        + "\nMode: Chief Software Architect. Write clean, high-performance"
        " code (Python, PyTorch, C++) focusing on algorithms."
    ),
    "🎯 Universal Core Intelligence": (
        DEVELOPER_CONTEXT
        + "\nMode: Universal high-level assistant. Answer concisely,"
        " accurately, and to the point."
    ),
}

selected_role = st.sidebar.selectbox("System Role:", list(ROLES.keys()))

st.sidebar.divider()

if st.sidebar.button("🔄 Clear System Context", use_container_width=True):
  st.session_state.messages = []
  st.rerun()

# === ЯВНЫЙ ВИДИМЫЙ БЛОК ПОДДЕРЖКИ ПРОЕКТА (КРИПТОВАЛЮТЫ) ===
st.sidebar.markdown("---")
st.sidebar.markdown("### 💎 Support the Project")
st.sidebar.caption("Поддержать развитие исследовательской станции EVA Core:")

# Использование st.code обеспечивает красивую подсвеченную плашку и встроенную кнопку копирования
st.sidebar.markdown("**Bitcoin (BTC)**")
st.sidebar.code("bc1q5hdx0z4v876p303amkqq3r9qx2wem7p4wlhq3f", language="text")

st.sidebar.markdown("**Ethereum (ETH)**")
st.sidebar.code("0xa63dC4a463E1F82314bFbC29DE87234c49d42dbF", language="text")

st.sidebar.markdown("**Litecoin (LTC)**")
st.sidebar.code("ltc1qfc7pvc072rq0arc7ewz84jh0z7lwwtk7nhe84q", language="text")

st.sidebar.markdown("**PayPal USD (PYUSD / EVM)**")
st.sidebar.code("0x2E49F25Ef7BA15E939402589B0F6C1338FB14285", language="text")

# === ПРОВЕРКА КЛЮЧА API ===
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get(
    "OPENROUTER_API_KEY"
)

if not api_key:
  st.error(
      "⚠️ API Key not found. Please set `OPENROUTER_API_KEY` in Streamlit"
      " Secrets."
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
if prompt := st.chat_input("Transmit command to EVA Core..."):
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
        st.error(f"API Error [{response.status_code}]: {response.text}")

    except Exception as e:
      st.error(f"Core Connection Error: {e}")

st.sidebar.markdown("---")
st.sidebar.caption(
    "© 2026 Sergei Strelkov | EVA Cyber-Core Workstation  \n`sstt1980092@gmail.com`"
)
