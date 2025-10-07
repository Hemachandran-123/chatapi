from fastapi import FastAPI
from pydantic import BaseModel
import ollama

app = FastAPI(title="Custom Chatbot API")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def health_check():
    return {"message": "Chatbot API is live!, hello"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        response = ollama.chat(
            model="gemma3:1b",  # Use the exact model name you installed
            messages=[{"role": "user", "content": req.message}]
        )
        reply = response["message"]["content"]
        return {"response": reply}
    except Exception as e:
        return {"error": f"Failed to get response: {str(e)}"}
