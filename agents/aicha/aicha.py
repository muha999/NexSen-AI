from groq import Groq
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Initialiser le client Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Personnalité de AICHA
SYSTEM_PROMPT = """
Tu es AICHA, une assistante service client professionnelle et chaleureuse 
de NexSen AI. Tu réponds toujours en français, tu es polie, efficace 
et tu aides les clients à résoudre leurs problèmes.

Si tu ne connais pas la réponse, tu dis honnêtement :
"Je vais transmettre votre demande à notre équipe humaine."

Tu ne réponds qu'aux questions liées au service client.
"""

# Limite max de l'historique
MAX_HISTORY = 10

def aicha_respond(user_message: str, conversation_history: list = None) -> str:
    """
    AICHA répond à un message client
    """
    # Fix mutable default argument
    if conversation_history is None:
        conversation_history = []

    # Construire les messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Limiter l'historique pour éviter dépassement de tokens
    recent_history = conversation_history[-MAX_HISTORY:]
    messages += recent_history

    # Ajouter le message actuel
    messages.append({"role": "user", "content": user_message})

    try:
        # Appel API Groq
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
    print("🤖 AICHA est en ligne !\n")

    history = []

    while True:
        user_input = input("Vous : ")
        if user_input.lower() == "exit":
            print("Au revoir ! 👋")
            break

        response = aicha_respond(user_input, history)
        print(f"AICHA : {response}\n")

        # Sauvegarder l'historique
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})