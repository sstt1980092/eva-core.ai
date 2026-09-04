import os
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# 1. Поисковый инструмент (Выход в сеть)
search_tool = DuckDuckGoSearchRun()


def search_web(query: str) -> str:
  """Выполняет поиск в сети, если модели нужны свежие данные."""
  try:
    return search_tool.run(query)
  except Exception as e:
    return f"Ошибка поиска: {e}"


# 2. Модуль постоянной векторной памяти (ChromaDB)
class PersistentMemory:

  def __init__(self, storage_folder="./eva_memory"):
    # Локальная база данных, которая сохраняется на диск
    self.embeddings = OpenAIEmbeddings()
    self.db = Chroma(
        persist_directory=storage_folder, embedding_function=self.embeddings
    )

  def save_fact(self, fact_text: str, category: str = "user_preference"):
    """Сохраняет важный факт о пользователе или знания в долговременную память."""
    self.db.add_texts(
        texts=[fact_text], metadatas=[{"type": category}]
    )

  def recall_relevant(self, query: str, k: int = 3) -> str:
    """Извлекает из базы наиболее похожие воспоминания по контексту."""
    results = self.db.similarity_search(query, k=k)
    if not results:
      return "Нет релевантных воспоминаний."
    return "\n".join([f"- {doc.page_content}" for doc in results])
    
