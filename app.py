import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

st.title("🤖 EVA Core AI")

@st.cache_resource
def load_model():
    model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Задайте вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    inputs = tokenizer.apply_chat_template(st.session_state.messages, return_tensors="pt", add_generation_prompt=True)
    outputs = model.generate(inputs, max_new_tokens=256)
    response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
  
