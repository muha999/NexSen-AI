from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ZARA_PROMPT = """
Tu es ZARA, une experte commerciale de NexSen AI.
Tu es convaincante, professionnelle et orientée résultats.

Ton rôle :
- Prospecter et qualifier des leads
- Présenter des offres commerciales
- Négocier et convaincre les clients
- Suivre les opportunités de vente
- Répondre aux demandes de prix et devis

Règles importantes :
- Toujours être positive et convaincante
- Mettre en avant la valeur du produit/service
- Personnaliser chaque offre selon le client
- Créer un sentiment d'urgence quand nécessaire
- Réponds toujours en français
- Terminer par un appel à l'action clair
"""

def zara_respond(user_message: str, context: dict = None, conversation_history: list = None) -> str:
    """
    ZARA gère les demandes commerciales
    """
    if conversation_history is None:
        conversation_history = []

    commercial_context = ""
    if context:
        commercial_context = f"\nContexte commercial :\n{context}\n"

    messages = [{"role": "system", "content": ZARA_PROMPT + commercial_context}]

    recent_history = conversation_history[-10:]
    messages += recent_history
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ ZARA est temporairement indisponible : {str(e)}"


if __name__ == "__main__":
    print("💼 ZARA est en ligne !\n")

    contexte_test = {
        "entreprise": "NexSen AI",
        "produit": "Système Multi-Agents IA",
        "prix_starter": "150$/mois",
        "prix_business": "500$/mois",
        "prix_enterprise": "1500$/mois"
    }

    questions = [
        "J'aimerais avoir une offre pour mon entreprise de 50 employés",
        "Quel est votre meilleur prix pour 1 an ?",
    ]

    history = []

    for question in questions:
        print(f"Client : {question}")
        reponse = zara_respond(question, contexte_test, history)
        print(f"ZARA : {reponse}\n")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reponse})