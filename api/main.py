from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.aicha.aicha import aicha_respond
from agents.ibrahima.ibrahima import ibrahima_evaluate

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
    evaluation: Optional[dict] = None

@app.get("/health")
def health():
    return {"status": "NexSen AI is running 🚀", "agents": ["AICHA", "IBRAHIMA"]}

@app.post("/aicha/chat", response_model=ChatResponse)
def chat_with_aicha(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]
    
    # AICHA répond
    response = aicha_respond(request.message, history)
    
    # IBRAHIMA évalue
    evaluation = ibrahima_evaluate(request.message, response)
    
    # Si score trop bas AICHA reformule une fois
    if evaluation.get("score", 10) < 5:
        response = aicha_respond(
            request.message + " (Reformule de façon plus précise et polie)",
            history
        )
    
    return ChatResponse(response=response, agent="AICHA", evaluation=evaluation)

@app.get("/ibrahima/evaluate")
def get_last_evaluation():
    return {"message": "IBRAHIMA surveille toutes les conversations 👁️"}