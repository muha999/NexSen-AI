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
from agents.fabi.fabi import fabi_analyze, fabi_check_produits
from agents.zara.zara import zara_respond
from agents.dija.dija import dija_respond

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

# Signaux qui indiquent qu'AICHA ne peut pas répondre seule
SIGNAUX_TRANSMISSION = [
    "transmettre", "équipe humaine", "je vais vérifier",
    "je n'ai pas", "pas d'informations", "pas accès"
]

@app.get("/health")
def health():
    return {
        "status": "NexSen AI is running 🚀",
        "agents": ["MUHA", "AICHA", "FABI", "ZARA", "DIJA", "IBRAHIMA"]
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]

    # MUHA analyse et route
    routing = muha_route(request.message)
    agent_name = routing.get("agent", "AICHA")
    message_transforme = routing.get("message_transforme", request.message)

    # Chaque agent répond selon son domaine
    if agent_name == "AICHA":
        response = aicha_respond(message_transforme, history)

        # MUHA détecte si AICHA bloque sur une question produit
        response_lower = response.lower()
        if any(signal in response_lower for signal in SIGNAUX_TRANSMISSION):
            # MUHA appelle FABI pour vérifier les produits
            info_produits = fabi_check_produits(request.message, history)

            # MUHA redonne le contexte enrichi à AICHA
            prompt_enrichi = (
                f"{request.message}\n\n"
                f"Informations internes de FABI (NE PAS mentionner l'ID, "
                f"reformule de façon concise et chaleureuse pour le client) :\n"
                f"{info_produits}"
            )
            response = aicha_respond(prompt_enrichi, history)

    elif agent_name == "FABI":
        response = fabi_analyze(message_transforme, None, history)
    elif agent_name == "ZARA":
        response = zara_respond(message_transforme, None, history)
    elif agent_name == "DIJA":
        response = dija_respond(message_transforme, None, history)
    else:
        response = aicha_respond(message_transforme, history)

    # IBRAHIMA évalue
    evaluation = ibrahima_evaluate(request.message, response, agent_name)

    return ChatResponse(
        response=response,
        agent=agent_name,
        evaluation=evaluation,
        routing=routing
    )

@app.post("/aicha/chat", response_model=ChatResponse)
def chat_with_aicha(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]
    response = aicha_respond(request.message, history)
    evaluation = ibrahima_evaluate(request.message, response)
    return ChatResponse(response=response, agent="AICHA", evaluation=evaluation)

@app.get("/ibrahima/evaluate")
def get_last_evaluation():
    return {"message": "IBRAHIMA surveille toutes les conversations 👁️"}