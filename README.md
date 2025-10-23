Custom AI Chatbot System
This project is a fully functional local AI chatbot that runs seamlessly on your machine — no cloud APIs required!
It combines the power of:

FastAPI → Backend API for chat handling

Streamlit → Frontend interface for real-time chat

Ollama → Local LLMs for natural language generation

MySQL + SQLAlchemy → Persistent message storage

The chatbot allows users to interact with a locally hosted model such as gemma3:1b, while logging all user and bot messages into a MySQL database.

🧩 Features

✅ Local inference using Ollama (privacy-friendly)
✅ Real-time chat UI with Streamlit
✅ FastAPI backend serving structured API responses
✅ Message history stored in MySQL using SQLAlchemy ORM
✅ Threaded backend + frontend integration (single-file execution)
✅ Easy to customize for different LLMs or data sources

Project Structure
.
├── combined_app.py        # Main script (FastAPI + Streamlit + MySQL)
├── requirements.txt       # Dependencies
├── images/
│   └── demo.png           # Screenshot or UI image
└── README.md

This isn’t just a project — it’s a reflection of curiosity, consistency, and the drive to turn ideas into impact.
