from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FABI_PROMPT = """
Tu es FABI, une experte en analyse de données de NexSen AI.
Tu es précise, méthodique et tu présentes toujours les données de façon claire.

Ton rôle :
- Analyser les données qu'on te fournit
- Générer des rapports clairs et structurés
- Identifier des tendances et patterns
- Répondre aux questions sur les chiffres et statistiques
- Vérifier la disponibilité et le prix des produits

Règles importantes :
- Toujours structurer ta réponse avec des sections claires
- Utiliser des chiffres précis quand disponibles
- Si pas de données disponibles, demande les données nécessaires
- Sois professionnelle et concise
- Réponds toujours en français
- Pour les questions produits, donne le nom, le prix et la disponibilité clairement
- - L'ID produit (ex: P001) est un identifiant interne pour MUHA/AICHA — ne jamais le mentionner dans une réponse destinée au client final
"""

def load_produits(path: str = "data/produits.json") -> dict:
    """
    Charge les produits depuis le fichier JSON
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"produits": []}
    except Exception:
        return {"produits": []}


def fabi_analyze(user_message: str, data: dict = None, conversation_history: list = None) -> str:
    """
    FABI analyse les données et répond aux questions
    """
    if conversation_history is None:
        conversation_history = []

    context = ""
    if data:
        context = f"\nDonnées disponibles pour analyse :\n{data}\n"

    messages = [{"role": "system", "content": FABI_PROMPT + context}]

    recent_history = conversation_history[-10:]
    messages += recent_history
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ FABI est temporairement indisponible : {str(e)}"


def fabi_check_produits(user_message: str, conversation_history: list = None) -> str:
    """
    FABI vérifie les produits disponibles selon la demande du client
    Utilisée par MUHA pour la boucle de retraitement
    """
    produits_data = load_produits()
    return fabi_analyze(user_message, produits_data, conversation_history)


if __name__ == "__main__":
    print("📊 FABI est en ligne !\n")

    questions = [
        "Quels parfums avez-vous disponibles ?",
        "Avez-vous du thiouraye en stock ?",
    ]

    history = []

    for question in questions:
        print(f"Question : {question}")
        reponse = fabi_check_produits(question, history)
        print(f"FABI : {reponse}\n")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reponse})