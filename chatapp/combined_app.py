import threading
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import streamlit as st
import requests
import time
import ollama

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# --- Database setup with SQLite (works locally & on Streamlit Cloud) ---
DATABASE_URL = "sqlite:///chatbot.db"

# SQLite requires this option to work with multithreading (FastAPI + Streamlit)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(10), index=True)  # "user" or "bot"
    content = Column(String(2000))
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- FastAPI app setup ---
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "FastAPI Chatbot API running"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    db = SessionLocal()
    try:
        # Save user's message in DB
        user_msg = ChatMessage(role="user", content=req.message)
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        # Generate bot response from Ollama
        response = ollama.chat(
            model="gemma3:1b",
            messages=[{"role": "user", "content": req.message}]
        )
        reply = response["message"]["content"]

        # Save bot response into DB
        bot_msg = ChatMessage(role="bot", content=reply)
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)

        return {"response": reply}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to get response: {str(e)}"}
    finally:
        db.close()

def run_api():
    uvicorn.run(app, host="127.0.0.1", port=8000)

# --- Start FastAPI in background thread ---
if "api_thread" not in st.session_state:
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    st.session_state.api_thread = api_thread
    time.sleep(1)

# --- Streamlit UI ---
st.title("💬 Chatbot with SQLite Stored History")

# Initialize chat message list if missing
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize sending flag to prevent double sends
if "is_sending" not in st.session_state:
    st.session_state.is_sending = False

def send_message(message):
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json={"message": message})
        if response.status_code == 200:
            return response.json().get("response")
        else:
            return f"Error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def clear_history():
    st.session_state.messages = []

# Clear chat history button
if st.button("🧹 Clear Chat History"):
    clear_history()

def send_message_action():
    if st.session_state.is_sending:
        return  # Prevent concurrent sends
    user_input = st.session_state.input_text.strip()
    if not user_input:
        return
    st.session_state.is_sending = True

    # Append user message
    st.session_state.messages.append(("user", user_input))

    # Send to backend and get bot response
    bot_response = send_message(user_input)
    st.session_state.messages.append(("bot", bot_response))

    st.session_state.is_sending = False

# Input box with Enter to send
st.text_input(
    "Type your message and press Enter",
    key="input_text",
    on_change=send_message_action,
    value="",
    placeholder="Type your message here...",
    disabled=st.session_state.is_sending
)

# Send button for mouse click send
if st.button("Send", disabled=st.session_state.is_sending):
    send_message_action()

# Display chat messages
for sender, msg in st.session_state.messages:
    if sender == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")
