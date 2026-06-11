from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.aicha.aicha import aicha_respond
from agents.ibrahima.ibrahima import ibrahima_evaluate
from agents.muha.muha import muha_route

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
    routing: Optional[dict] = None

@app.get("/health")
def health():
    return {
        "status": "NexSen AI is running 🚀",
        "agents": ["MUHA", "AICHA", "IBRAHIMA", "FABI", "ZARA", "DIJA"]
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]

    # MUHA analyse et route
    routing = muha_route(request.message)
    agent_name = routing.get("agent", "AICHA")
    message_transforme = routing.get("message_transforme", request.message)

    # Pour l instant seule AICHA est codée
    if agent_name == "AICHA":
        response = aicha_respond(message_transforme, history)
    elif agent_name == "FABI":
        response = f"📊 FABI est en cours de développement. Votre demande d'analyse a été enregistrée."
    elif agent_name == "ZARA":
        response = f"💼 ZARA est en cours de développement. Votre demande commerciale a été enregistrée."
    elif agent_name == "DIJA":
        response = f"👥 DIJA est en cours de développement. Votre demande de recrutement a été enregistrée."
    else:
        response = aicha_respond(message_transforme, history)

    # IBRAHIMA évalue
    evaluation = ibrahima_evaluate(request.message, response, agent_name)

    # Si score trop bas reformuler
    if evaluation.get("score", 10) < 5 and agent_name == "AICHA":
        response = aicha_respond(
            message_transforme + " (Reformule de façon plus précise et polie)",
            history
        )

    return ChatResponse(
        response=response,
        agent=agent_name,
        evaluation=evaluation,
        routing=routing
    )

# Ancienne route AICHA directe — gardée pour compatibilité
@app.post("/aicha/chat", response_model=ChatResponse)
def chat_with_aicha(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]
    response = aicha_respond(request.message, history)
    evaluation = ibrahima_evaluate(request.message, response)
    return ChatResponse(response=response, agent="AICHA", evaluation=evaluation)

@app.get("/ibrahima/evaluate")
def get_last_evaluation():
    return {"message": "IBRAHIMA surveille toutes les conversations 👁️"}