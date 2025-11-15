import streamlit as st
import requests
import json

st.set_page_config(page_title="Intelligent Underwriting MAS ")

st.title("🚗 Intelligent Underwriting mas")

# Session state storage
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
user_input = st.chat_input("Ask me anything…")

if user_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # ----- BACKEND REQUEST -----
    # Replace with your MAS endpoint (FastAPI, Flask, etc.)
    # Example:
    # response = requests.post("http://localhost:8000/mas", json={"message": user_input})
    
    # For demo:
    response_text = f"You said: {user_input} (MAS response goes here)"

    # Store assistant response
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    with st.chat_message("assistant"):
        st.write(response_text)
