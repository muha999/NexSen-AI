from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.aicha.aicha import aicha_respond

app = FastAPI(title="NexSen AI", description="Multi-Agent AI System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    response: str
    agent: str

@app.get("/health")
def health():
    return {"status": "NexSen AI is running 🚀", "agents": ["AICHA"]}

@app.post("/aicha/chat", response_model=ChatResponse)
def chat_with_aicha(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]
    response = aicha_respond(request.message, history)
    return ChatResponse(response=response, agent="AICHA")