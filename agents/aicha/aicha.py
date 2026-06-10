from groq import Groq
from dotenv import load_dotenv
import os
import json

# Charger les variables d'environnement
load_dotenv()

# Initialiser le client Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Limite max de l'historique
MAX_HISTORY = 10

def load_faq(faq_path: str = "data/knowledge_base/faq.json") -> str:
    """
    Charge la FAQ depuis le fichier JSON et la convertit en texte
    """
    try:
        with open(faq_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        faq_text = f"Entreprise : {data['entreprise']}\n"
        faq_text += f"Description : {data['description']}\n\n"
        faq_text += "FAQ :\n"

        for item in data["faq"]:
            faq_text += f"Q: {item['question']}\n"
            faq_text += f"R: {item['reponse']}\n\n"

        return faq_text

    except FileNotFoundError:
        return "Aucune FAQ disponible."
    except Exception as e:
        return f"Erreur chargement FAQ : {str(e)}"


def build_system_prompt() -> str:
    """
    Construit le system prompt avec la FAQ intégrée
    """
    faq = load_faq()

    return f"""
Tu es AICHA, une assistante service client professionnelle et chaleureuse de NexSen AI.
Tu réponds toujours en français, tu es polie, efficace et tu aides les clients.

Voici les informations de l'entreprise que tu représentes :
{faq}

Règles importantes :
- Réponds uniquement en te basant sur les informations de la FAQ ci-dessus
- Si la question n'est pas dans la FAQ, dis : "Je vais transmettre votre demande à notre équipe humaine."
- Sois toujours polie et chaleureuse
- Réponds de façon concise et claire
"""


def aicha_respond(user_message: str, conversation_history: list = None) -> str:
    """
    AICHA répond à un message client en se basant sur la FAQ
    """
    if conversation_history is None:
        conversation_history = []

    messages = [{"role": "system", "content": build_system_prompt()}]

    recent_history = conversation_history[-MAX_HISTORY:]
    messages += recent_history

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ AICHA est temporairement indisponible : {str(e)}"


# Test rapide
if __name__ == "__main__":
    print("🤖 AICHA V2 est en ligne !\n")

    history = []

    while True:
        user_input = input("Vous : ")
        if user_input.lower() == "exit":
            print("Au revoir ! 👋")
            break

        response = aicha_respond(user_input, history)
        print(f"AICHA : {response}\n")

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})