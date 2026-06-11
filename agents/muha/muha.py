from groq import Groq
from dotenv import load_dotenv
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MUHA_PROMPT = """
Tu es MUHA, l'agent orchestrateur de NexSen AI.
Ton rôle est d'analyser chaque demande et de décider quel agent est le plus adapté.

Les agents disponibles sont :
- AICHA : service client, questions sur commandes, livraisons, retours, paiements
- FABI : analyse de données, rapports, statistiques, chiffres
- ZARA : commercial, ventes, prospects, offres, negociation
- DIJA : recrutement, CVs, candidatures, entretiens, emploi

Tu réponds UNIQUEMENT en JSON avec ce format exact :
{
  "agent": "<nom de l agent : AICHA, FABI, ZARA ou DIJA>",
  "raison": "<pourquoi tu as choisi cet agent>",
  "priorite": "<haute, moyenne ou basse>",
  "message_transforme": "<le message reformulé pour l agent>"
}
"""

def muha_route(user_message: str) -> dict:
    """
    MUHA analyse la demande et choisit le bon agent
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": MUHA_PROMPT},
                {"role": "user", "content": f"Analyse cette demande et choisis le bon agent : {user_message}"}
            ],
            temperature=0.2,
            max_tokens=300
        )

        raw = response.choices[0].message.content.strip()

        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        result = json.loads(raw)
        return result

    except Exception as e:
        return {
            "agent": "AICHA",
            "raison": "Agent par défaut — erreur de routage",
            "priorite": "moyenne",
            "message_transforme": user_message
        }


if __name__ == "__main__":
    print("🧠 MUHA est en ligne !\n")

    tests = [
        "J'ai un problème avec ma commande",
        "Je veux voir les statistiques de ventes du mois",
        "Je cherche un développeur Python senior",
        "J'aimerais avoir une offre pour 50 unités"
    ]

    for message in tests:
        print(f"Message : {message}")
        decision = muha_route(message)
        print(f"→ Agent choisi : {decision['agent']}")
        print(f"→ Raison : {decision['raison']}")
        print(f"→ Priorité : {decision['priorite']}")
        print()