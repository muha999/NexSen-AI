from groq import Groq
from dotenv import load_dotenv
import os

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
- Donner des recommandations basées sur les données

Règles importantes :
- Toujours structurer ta réponse avec des sections claires
- Utiliser des chiffres précis quand disponibles
- Si pas de données disponibles, demande les données nécessaires
- Sois professionnelle et concise
- Réponds toujours en français
"""

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


if __name__ == "__main__":
    print("📊 FABI est en ligne !\n")

    donnees_test = {
        "ventes": {
            "janvier": 150000,
            "fevrier": 175000,
            "mars": 210000,
            "avril": 195000,
            "mai": 230000
        },
        "clients": 342,
        "produit_top": "Parfum Luxe",
        "region_top": "Dakar"
    }

    questions = [
        "Analyse les ventes et donne moi un rapport",
        "Quelle est la tendance générale des ventes ?",
    ]

    history = []

    for question in questions:
        print(f"Question : {question}")
        reponse = fabi_analyze(question, donnees_test, history)
        print(f"FABI : {reponse}\n")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reponse})