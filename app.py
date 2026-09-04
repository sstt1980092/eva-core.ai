import json
import os
import requests
import streamlit as st
from duckduckgo_search import DDGS

# ==============================================================================
# 1. КОНФИГУРАЦИЯ СТРАНИЦЫ И СТИЛИЗАЦИЯ EVA CYBER-CORE
# ==============================================================================
st.set_page_config(
    page_title="EVA Core AI | Autonomous Research Workstation",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
        font-size: 26px;
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

# ==============================================================================
# 2. МОДУЛЬ ПАМЯТИ (PERSISTENT MEMORY LEDGER)
# ==============================================================================
MEMORY_FILE = "eva_memory_ledger.json"


def load_memory():
  if os.path.exists(MEMORY_FILE):
    try:
      with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return []
  return []


def save_memory_fact(fact: str):
  facts = load_memory()
  if fact not in facts:
    facts.append(fact)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
      json.dump(facts, f, ensure_ascii=False, indent=2)


def clear_memory_store():
  if os.path.exists(MEMORY_FILE):
    os.remove(MEMORY_FILE)


# ==============================================================================
# 3. БЕСПЛАТНЫЙ МОДУЛЬ ВЕБ-ПОИСКА (DUCKDUCKGO ENGINE)
# ==============================================================================
def search_duckduckgo(query: str, max_results: int = 4) -> str:
  """Автономный поиск данных в сети через DuckDuckGo (без использования платного OpenRouter API)."""
  try:
    results = []
    with DDGS() as ddgs:
      for r in ddgs.text(query, max_results=max_results):
        results.append(f"• [{r['title']}]({r['href']}): {r['body']}")
    if results:
      return "\n".join(results)
  except Exception as e:
    return f"Ошибка при обращении к поисковому движку: {e}"
  return "Информация по запросу не найдена."


# ==============================================================================
# 4. ШАПКА ИНТЕРФЕЙСА
# ==============================================================================
st.markdown(
    """
    <div class="eva-header">
        <div class="eva-title">
            <span class="core-pulse"></span> ⚛️ EVA CORE AI <span style="font-size:14px; color:#8b949e; font-weight:400;">v3.0 Autonomous Workstation</span>
        </div>
        <div class="eva-subtitle">
            Autonomous Research Intelligence | Chief Architect: <span class="developer-tag">SERGEI STRELKOV</span> (sstt1980092@gmail.com)
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 5. БОКОВАЯ ПАНЕЛЬ С УПРАВЛЕНИЕМ МОДУЛЯМИ АВТОНОМНОСТИ
# ==============================================================================
st.sidebar.markdown("### 🎛️ AI Core Control")
st.sidebar.markdown(
    "**Architect:** Sergei Strelkov\n📧 `sstt1980092@gmail.com`"
)
st.sidebar.divider()

st.sidebar.markdown("### 🧠 Autonomous Modules")
enable_web_search = st.sidebar.checkbox(
    "🌐 Поиск в реальном времени (Web Search)", value=True
)
enable_persistent_memory = st.sidebar.checkbox(
    "💾 Долговременная память (Memory Ledger)", value=True
)

st.sidebar.divider()

st.sidebar.markdown("### 📝 Memory Ledger")
saved_facts = load_memory()
st.sidebar.caption(f"Сохранено фактов в базе: **{len(saved_facts)}**")

new_fact_input = st.sidebar.text_input("Добавить факт вручную:")
if st.sidebar.button("💾 Запомнить факт", use_container_width=True):
  if new_fact_input.strip():
    save_memory_fact(new_fact_input.strip())
    st.sidebar.success("Факт зафиксирован!")
    st.rerun()

if saved_facts:
  with st.sidebar.expander("🔍 Посмотреть сохраненные факты"):
    for i, fact in enumerate(saved_facts, 1):
      st.write(f"{i}. {fact}")

if st.sidebar.button("🗑️ Очистить всю память", use_container_width=True):
  clear_memory_store()
  st.sidebar.info("Память очищена.")
  st.rerun()

st.sidebar.divider()

AVAILABLE_MODELS = {
    "🌐 OpenRouter Free Router (Auto-Select)": "openrouter/free",
    "🧠 DeepSeek R1 Free (Logic & Reasoning)": "deepseek/deepseek-r1:free",
    "⚡ Google Gemini 2.0 Flash Exp (Speed & Multimodal)": (
        "google/gemini-2.0-flash-exp:free"
    ),
    "💻 Qwen 2.5 72B Instruct (Code & Analytics)": (
        "qwen/qwen-2.5-72b-instruct:free"
    ),
    "🚀 MiniMax M3 Free (Fast / Long Context)": "minimax/minimax-m3:free",
    "🌪️ Mistral 7B Instruct v0.3 (Stable Fast)": (
        "mistralai/mistral-7b-instruct:free"
    ),
    "🛡️ NVIDIA Nemotron 3 Ultra (Deep Analysis)": (
        "nvidia/nemotron-3-ultra-550b-a55b:free"
    ),
}

selected_model_label = st.sidebar.selectbox(
    "Select AI Core Model:", list(AVAILABLE_MODELS.keys())
)
model_id = AVAILABLE_MODELS[selected_model_label]

st.sidebar.divider()

if st.sidebar.button("🔄 Clear Active Chat Session", use_container_width=True):
  st.session_state.messages = []
  st.rerun()

# ==============================================================================
# 6. РАЗДЕЛ ПОДДЕРЖКИ ПРОЕКТА (КРИПТОВАЛЮТЫ)
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 💎 Support the Project")
st.sidebar.caption("Поддержать развитие исследовательского ядра EVA Core:")

st.sidebar.markdown("**Bitcoin (BTC)**")
st.sidebar.code("bc1q5hdx0z4v876p303amkqq3r9qx2wem7p4wlhq3f", language="text")

st.sidebar.markdown("**Ethereum (ETH)**")
st.sidebar.code("0xa63dC4a463E1F82314bFbC29DE87234c49d42dbF", language="text")

st.sidebar.markdown("**Litecoin (LTC)**")
st.sidebar.code("ltc1qfc7pvc072rq0arc7ewz84jh0z7lwwtk7nhe84q", language="text")

st.sidebar.markdown("**PayPal USD (PYUSD / EVM)**")
st.sidebar.code("0x2E49F25Ef7BA15E939402589B0F6C1338FB14285", language="text")

# ==============================================================================
# 7. ОСНОВНАЯ ЛОГИКА И ВЗАИМОДЕЙСТВИЕ
# ==============================================================================
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get(
    "OPENROUTER_API_KEY"
)

if not api_key:
  st.error(
      "⚠️ API Key not found. Please set `OPENROUTER_API_KEY` in Streamlit"
      " Secrets or Environment Variables."
  )
  st.stop()

if "messages" not in st.session_state:
  st.session_state.messages = []

for msg in st.session_state.messages:
  icon = "👤" if msg["role"] == "user" else "⚛️"
  with st.chat_message(msg["role"], avatar=icon):
    st.write(msg["content"])

if prompt := st.chat_input("Transmit command to EVA Core..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user", avatar="👤"):
    st.write(prompt)

  if any(
      kw in prompt.lower() for kw in ["запомни", "сохрани факт", "зафиксируй"]
  ):
    save_memory_fact(prompt)
    st.toast("Факт сохранен в долговременную память!", icon="💾")

  memory_context_str = ""
  if enable_persistent_memory:
    facts = load_memory()
    if facts:
      memory_context_str = (
          "\n[PERSISTENT MEMORY STORE - KNOWN FACTS]:\n"
          + "\n".join([f"- {f}" for f in facts])
          + "\n"
      )

  # --- Автономный поиск DuckDuckGo (полностью бесплатный) ---
  web_context_str = ""
  search_trigger_keywords = [
      "новости",
      "курс",
      "свежие",
      "найди",
      "погода",
      "сегодня",
      "2026",
      "цена",
      "актуальный",
      "что происходит",
      "поиск",
  ]
  if enable_web_search and any(
      kw in prompt.lower() for kw in search_trigger_keywords
  ):
    with st.status("🔍 Выход в сеть и поиск данных...", expanded=False) as status:
      search_res = search_duckduckgo(prompt)
      web_context_str = (
          f"\n[REAL-TIME WEB DATA SEARCH RESULTS]:\n{search_res}\n"
      )
      status.update(
          label="✅ Поисковые данные получены!", state="complete", expanded=False
      )

  system_instruction = f"""
SYSTEM CONTEXT & DEVELOPER PROFILE:
You are EVA Core AI, an advanced cybernetic research intelligence created by Sergei Strelkov (born September 10, 1980, e-mail: sstt1980092@gmail.com).

CRITICAL INSTRUCTIONS:
1. ALWAYS detect the user's language and respond in the EXACT SAME language.
2. Use the persistent memory and real-time web results provided below to enrich and perfect your analysis.
3. Answer with maximum engineering depth, analytical rigor, and accuracy.

{memory_context_str}
{web_context_str}
"""

  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json",
      "HTTP-Referer": "https://eva-core-ai.streamlit.app",
      "X-Title": "EVA Core Workstation by Sergei Strelkov",
  }

  full_messages = [{"role": "system", "content": system_instruction}] + [
      {"role": m["role"], "content": m["content"]}
      for m in st.session_state.messages
  ]

  # Запрос без плагина OpenRouter 'web', чтобы не вызывать ошибку 402 Insufficient credits
  payload = {
      "model": model_id,
      "messages": full_messages,
      "temperature": 0.5,
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
