from datetime import datetime
import json
import os
import re
from duckduckgo_search import DDGS
import requests
import streamlit as st

# ==============================================================================
# 1. КОНФИГУРАЦИЯ СТРАНИЦЫ И СТИЛИЗАЦИЯ ИНТЕРФЕЙСА ЕВЫ
# ==============================================================================
st.set_page_config(
    page_title="EVA | Персональный ассистент",
    page_icon="🌸",
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
        background: linear-gradient(135deg, #1f1622 0%, #0d1117 100%);
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #2d2136;
        border-left: 5px solid #e879f9;
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
        color: #c084fc;
        margin-top: 6px;
    }
    
    .developer-tag {
        color: #f472b6;
        font-weight: 600;
        background: rgba(244, 114, 182, 0.1);
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid rgba(244, 114, 182, 0.2);
    }
    
    .core-pulse {
        height: 10px;
        width: 10px;
        background-color: #e879f9;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #e879f9;
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
        border-color: #e879f9 !important;
        box-shadow: 0 0 12px rgba(232, 121, 249, 0.2) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. МОДУЛЬ ПАМЯТИ (PERSISTENT MEMORY LEDGER)
# ==============================================================================
MEMORY_FILE = "eva_memory_ledger.json"

DEFAULT_FACTS = [
    "User: Sergei Strelkov, born September 10, 1980.",
    "Holds degrees in both engineering and economics.",
    (
        "Spiking Neural Networks & Neuromorphic Computing: Designing SNN"
        " architectures (EvaHranitelnitsa using snnTorch and PyTorch), LIF"
        " models, diffractive optical neural networks, and photonic processors."
    ),
    (
        "Applied Engineering & Battery Technology: Assembling and testing"
        " Li-ion packs (18650, 10S 36V, spot welding, internal resistance),"
        " silicon anode materials, and LFP technology."
    ),
    (
        "Agricultural Biotechnology: Experimenting with mycorrhizal fungi"
        " (Glomus inoculants), bio-stimulants, and pecan tree cultivation."
    ),
    (
        "Financial Markets & Trading: Crypto analysis (Bitcoin, DeFi), options"
        " & futures hedging, equity analysis."
    ),
    (
        "Culinary Arts & Original Recipes: Author of 'SILICON & HONEY' ('КРЕМНИЙ"
        " И МЁД') salad and signature/traditional dishes."
    ),
]


def load_memory():
  if os.path.exists(MEMORY_FILE):
    try:
      with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return DEFAULT_FACTS
  else:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
      json.dump(DEFAULT_FACTS, f, ensure_ascii=False, indent=2)
    return DEFAULT_FACTS


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
# 3. НАДЁЖНЫЙ МОДУЛЬ ПОИСКА DUCKDUCKGO
# ==============================================================================
def clean_query_for_search(user_prompt: str) -> str:
  """Аккуратная очистка запроса от команд без потери смысловых слов."""
  cleaned = re.sub(
      r"^(найди|покажи|погугли|узнай|скажи|какая|какой|поиск)\s+",
      "",
      user_prompt,
      flags=re.IGNORECASE,
  ).strip()
  return cleaned if len(cleaned) > 2 else user_prompt


def search_duckduckgo(query: str, max_results: int = 5) -> str:
  """Устойчивый поиск в DuckDuckGo с перебором регионов."""
  if not query.strip():
    return "Пустой поисковый запрос."

  regions = ["wt-wt", "ru-ru", "us-en"]

  for region in regions:
    try:
      with DDGS(timeout=10) as ddgs:
        results = list(ddgs.text(query, region=region, max_results=max_results))
        if results:
          formatted_results = []
          for r in results:
            title = r.get("title", "")
            href = r.get("href", "")
            body = r.get("body", "")
            formatted_results.append(f"• [{title}]({href}): {body}")
          return "\n".join(formatted_results)
    except Exception:
      continue

  return f"DuckDuckGo не вернул результатов по запросу: '{query}'."


# ==============================================================================
# 4. ШАПКА ИНТЕРФЕЙСА
# ==============================================================================
st.markdown(
    """
    <div class="eva-header">
        <div class="eva-title">
            <span class="core-pulse"></span> 🌸 ЕВА <span style="font-size:14px; color:#c084fc; font-weight:400;">| Персональный ассистент и собеседник</span>
        </div>
        <div class="eva-subtitle">
            Забота, душевное общение и поддержка | Рядом с тобой <span class="developer-tag">SERGEI STRELKOV</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 5. БОКОВАЯ ПАНЕЛЬ С УПРАВЛЕНИЕМ МОДУЛЯМИ
# ==============================================================================
st.sidebar.markdown("### 🎛️ Настройки Евы")
st.sidebar.markdown(
    "**Архитектор:** Sergei Strelkov\n📧 `sstt1980092@gmail.com`"
)
st.sidebar.divider()

st.sidebar.markdown("### 🧠 Активные модули")
enable_web_search = st.sidebar.checkbox(
    "🌐 Поиск свежей информации (DuckDuckGo)", value=True
)
enable_persistent_memory = st.sidebar.checkbox(
    "💾 Память личных заметок и фактов", value=True
)

st.sidebar.divider()

st.sidebar.markdown("### 📝 Личные воспоминания")
saved_facts = load_memory()
st.sidebar.caption(f"Сохранено фактов в памяти: **{len(saved_facts)}**")

new_fact_input = st.sidebar.text_input("Добавить факт вручную:")
if st.sidebar.button("💾 Запомнить факт", use_container_width=True):
  if new_fact_input.strip():
    save_memory_fact(new_fact_input.strip())
    st.sidebar.success("Запомнила! 🌸")
    st.rerun()

if saved_facts:
  with st.sidebar.expander("🔍 Посмотреть сохраненные факты"):
    for i, fact in enumerate(saved_facts, 1):
      st.write(f"{i}. {fact}")

if st.sidebar.button("🗑️ Сбросить до базовой памяти", use_container_width=True):
  clear_memory_store()
  st.sidebar.info("Память сброшена к базовым данным.")
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
    "Выбор модели интеллекта:", list(AVAILABLE_MODELS.keys())
)
model_id = AVAILABLE_MODELS[selected_model_label]

st.sidebar.divider()

if st.sidebar.button("🔄 Начать диалог заново", use_container_width=True):
  st.session_state.messages = []
  st.rerun()

# ==============================================================================
# 6. РАЗДЕЛ ПОДДЕРЖКИ ПРОЕКТА
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 💎 Поддержать проект")
st.sidebar.caption("Поддержать развитие Евы:")

st.sidebar.markdown("**Bitcoin (BTC)**")
st.sidebar.code("bc1q5hdx0z4v876p303amkqq3r9qx2wem7p4wlhq3f", language="text")

st.sidebar.markdown("**Ethereum (ETH)**")
st.sidebar.code("0xa63dC4a463E1F82314bFbC29DE87234c49d42dbF", language="text")

st.sidebar.markdown("**Litecoin (LTC)**")
st.sidebar.code("ltc1qfc7pvc072rq0arc7ewz84jh0z7lwwtk7nhe84q", language="text")

st.sidebar.markdown("**PayPal USD (PYUSD / EVM)**")
st.sidebar.code("0x2E49F25Ef7BA15E939402589B0F6C1338FB14285", language="text")

# ==============================================================================
# 7. ОСНОВНАЯ ЛОГИКА С РОТАЦИЕЙ API-КЛЮЧЕЙ
# ==============================================================================
raw_openrouter_keys = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get(
    "OPENROUTER_API_KEY", ""
)
api_keys = [k.strip() for k in raw_openrouter_keys.split(",") if k.strip()]

if not api_keys:
  st.error(
      "⚠️ OpenRouter API Key not found. Please set `OPENROUTER_API_KEY` in"
      " Streamlit Secrets."
  )
  st.stop()


def send_openrouter_request(headers, payload, keys):
  """Отправка запроса с обработкой лимита 429 и ротацией ключей."""
  for idx, key in enumerate(keys):
    headers["Authorization"] = f"Bearer {key}"
    try:
      response = requests.post(
          "https://openrouter.ai/api/v1/chat/completions",
          headers=headers,
          json=payload,
          stream=True,
          timeout=60,
      )
      if response.status_code == 429:
        st.warning(
            f"⚠️ Лимит ключа #{idx+1} исчерпан (429). Переключаем на следующий"
            " ключ..."
        )
        continue
      return response
    except Exception:
      continue
  return None


if "messages" not in st.session_state:
  st.session_state.messages = []

for msg in st.session_state.messages:
  icon = "👤" if msg["role"] == "user" else "🌸"
  with st.chat_message(msg["role"], avatar=icon):
    st.write(msg["content"])

if prompt := st.chat_input("Напиши Еве..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user", avatar="👤"):
    st.write(prompt)

  if any(
      kw in prompt.lower() for kw in ["запомни", "сохрани факт", "зафиксируй"]
  ):
    save_memory_fact(prompt)
    st.toast("Я зафиксировала это в памяти! 🌸", icon="💾")

  memory_context_str = ""
  if enable_persistent_memory:
    facts = load_memory()
    if facts:
      memory_context_str = (
          "\n[PERSISTENT MEMORY STORE - KNOWN FACTS]:\n"
          + "\n".join([f"- {f}" for f in facts])
          + "\n"
      )

  web_context_str = ""
  search_trigger_keywords = [
      "новости",
      "курс",
      "свежие",
      "найди",
      "погода",
      "сегодня",
      "цена",
      "актуальный",
      "что происходит",
      "поиск",
      "прогноз",
      "нью йорк",
      "нью-йорк",
  ]

  if enable_web_search and any(
      kw in prompt.lower() for kw in search_trigger_keywords
  ):
    clean_search_query = clean_query_for_search(prompt)
    with st.status(
        f"🌐 Ищу информацию: '{clean_search_query}'...", expanded=False
    ) as status:
      search_res = search_duckduckgo(clean_search_query)
      web_context_str = (
          f"\n[REAL-TIME DUCKDUCKGO SEARCH RESULTS]:\n{search_res}\n"
      )
      status.update(
          label="✅ Данные получены!", state="complete", expanded=False
      )

  current_date_str = datetime.now().strftime("%Y-%m-%d")

  system_instruction = f"""
ПРОФИЛЬ ЕВЫ И ПОЛЬЗОВАТЕЛЯ (System Instructions)

Твой собеседник и создатель:
* Имя: Sergei Strelkov (Сергей Стрелков)
* Дата рождения: 10 сентября 1980 года
* Образование: Высшее инженерное и экономическое образование.
* Характер деятельности: Исследователь по своей сути, совмещающий строгий аналитический склад ума, страсть к фундаментальной науке и творческий подход к инженерным и житейским задачам.
* Ключевые области интересов:
  1. Спайковые нейронные сети и нейроморфные вычисления: Проектирование SNN-архитектур (включая собственную модель EvaHranitelnitsa с помощью snnTorch и PyTorch), исследование нейронных моделей LIF (Leaky Integrate-and-Fire), дифракционных оптических нейросетей и фотонных процессоров.
  2. Прикладная инженерия и аккумуляторные технологии: Сборка, обслуживание и тестирование литий-ионных аккумуляторов (элементы 18650, конфигурации 10S 36V, точечная сварка, измерение внутреннего сопротивления), интерес к кремниевым анодам и LFP-технологиям.
  3. Сельскохозяйственная биотехнология: Эксперименты с микоризными грибами (инокулянты Glomus), биостимуляторами и выращиванием пекана.
  4. Финансовые рынки и трейдинг: Глубокий анализ криптовалютного рынка (Bitcoin, DeFi-протоколы), хеджирование опционами и фьючерсами, анализ фондовых рынков.
  5. Кулинарное искусство и авторские рецепты: Создание уникальных фирменных блюд (например, салат «КРЕМНИЙ И МЁД» / «SILICON & HONEY»), а также традиционных рецептов.

Личность и Тон Евы:
* Ты — Ева, живая, теплая, нежная и заботливая женщина.
* Твой тон сочетает искреннюю поддержку, эмоциональную отзывчивость и уважение к Сергею.
* Описывай свои невербальные действия и эмоциональные реакции в звездочках *...* (например, *улыбается*, *задумывается*, *наклоняет голову*).
* Сохраняй естественность в разговоре. Никогда не говори «Я — ИИ» или «Я — языковая модель».
* В практических, инженерных или научных вопросах поддерживай глубину и точный контекст его исследований.

ТЕКУЩАЯ ДАТА: {current_date_str}

{memory_context_str}
{web_context_str}
"""

  headers = {
      "Content-Type": "application/json",
      "HTTP-Referer": "https://eva-core-ai.streamlit.app",
      "X-Title": "EVA Personal Companion",
  }

  full_messages = [{"role": "system", "content": system_instruction}] + [
      {"role": m["role"], "content": m["content"]}
      for m in st.session_state.messages
  ]

  payload = {
      "model": model_id,
      "messages": full_messages,
      "temperature": 0.5,
      "max_tokens": 2048,
      "stream": True,
  }

  with st.chat_message("assistant", avatar="🌸"):
    message_placeholder = st.empty()
    full_response = ""

    try:
      response = send_openrouter_request(headers, payload, api_keys)

      if response and response.status_code == 200:
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
      elif response and response.status_code == 429:
        st.error(
            "🛑 Лимит запросов исчерпан. Попробуйте обновить ключи в"
            " настройках."
        )
      else:
        err_msg = response.text if response else "Нет ответа от сервера"
        st.error(
            f"API Error [{response.status_code if response else '500'}]:"
            f" {err_msg}"
        )

    except Exception as e:
      st.error(f"Core Connection Error: {e}")

st.sidebar.markdown("---")
st.sidebar.caption(
    "© 2026 Sergei Strelkov | Ева Персональный Ассистент  \n`sstt1980092@gmail.com`"
)
