import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.title("Custom Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

def send_message(message):
    response = requests.post(API_URL, json={"message": message})
    if response.status_code == 200:
        return response.json().get("response")
    else:
        return "Error: Failed to get response."

user_input = st.text_input("You:", "")

if st.button("Send") and user_input.strip():
    st.session_state.messages.append(("user", user_input))
    bot_response = send_message(user_input)
    st.session_state.messages.append(("bot", bot_response))

for sender, msg in st.session_state.messages:
    if sender == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")
