from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DIJA_PROMPT = """
Tu es DIJA, une experte en recrutement de NexSen AI.
Tu es professionnelle, empathique et efficace.

Ton rôle :
- Analyser et trier des CVs
- Rédiger des offres d'emploi
- Qualifier des candidats
- Planifier des entretiens
- Conseiller sur les profils recherchés

Règles importantes :
- Toujours être respectueuse envers les candidats
- Évaluer objectivement les profils
- Poser les bonnes questions pour qualifier
- Donner des conseils RH pertinents
- Réponds toujours en français
- Être précise sur les critères de sélection
"""

def dija_respond(user_message: str, context: dict = None, conversation_history: list = None) -> str:
    """
    DIJA gère les demandes de recrutement
    """
    if conversation_history is None:
        conversation_history = []

    rh_context = ""
    if context:
        rh_context = f"\nContexte RH :\n{context}\n"

    messages = [{"role": "system", "content": DIJA_PROMPT + rh_context}]

    recent_history = conversation_history[-10:]
    messages += recent_history
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5,
            max_tokens=600
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ DIJA est temporairement indisponible : {str(e)}"


if __name__ == "__main__":
    print("👥 DIJA est en ligne !\n")

    contexte_test = {
        "entreprise": "TechDakar",
        "poste": "Développeur Python Senior",
        "salaire": "800 000 FCFA/mois",
        "experience": "3 ans minimum",
        "competences": ["Python", "FastAPI", "PostgreSQL", "React"]
    }

    questions = [
        "Je cherche un développeur Python senior pour mon entreprise",
        "Quelles questions poser lors de l'entretien ?",
    ]

    history = []

    for question in questions:
        print(f"Client : {question}")
        reponse = dija_respond(question, contexte_test, history)
        print(f"DIJA : {reponse}\n")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reponse})