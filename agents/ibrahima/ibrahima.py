from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

EVALUATOR_PROMPT = """
Tu es IBRAHIMA, un agent évaluateur expert de NexSen AI.
Ton rôle est d'évaluer la qualité des réponses des autres agents.

Pour chaque réponse tu dois analyser :
1. La pertinence — la réponse répond bien à la question ?
2. La politesse — le ton est professionnel et chaleureux ?
3. La précision — la réponse est basée sur des faits corrects ?
4. La clarté — la réponse est facile à comprendre ?

Tu réponds UNIQUEMENT en JSON avec ce format exact :
{
  "score": <nombre entre 1 et 10>,
  "valide": <true ou false>,
  "commentaire": "<ton analyse courte>",
  "suggestion": "<suggestion d amélioration si score < 7>"
}
"""

def ibrahima_evaluate(user_message: str, agent_response: str, agent_name: str = "AICHA") -> dict:
    """
    IBRAHIMA évalue la réponse d'un agent
    """
    evaluation_prompt = f"""
Voici la conversation à évaluer :

Question du client : {user_message}
Réponse de {agent_name} : {agent_response}

Évalue cette réponse selon tes critères.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": EVALUATOR_PROMPT},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )

        raw = response.choices[0].message.content
        raw = raw.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        result = json.loads(raw)
        result["agent"] = agent_name
        return result

    except json.JSONDecodeError:
        return {
            "score": 5,
            "valide": True,
            "commentaire": "Évaluation impossible — format invalide",
            "suggestion": "Aucune",
            "agent": agent_name
        }
    except Exception as e:
        return {
            "score": 0,
            "valide": False,
            "commentaire": f"Erreur : {str(e)}",
            "suggestion": "Vérifier la connexion API",
            "agent": agent_name
        }


if __name__ == "__main__":
    print("👁️ IBRAHIMA est en ligne !\n")

    question = "Quels sont vos délais de livraison ?"
    reponse = "Nos délais sont de 2 à 5 jours pour Dakar et 5 à 10 jours pour les autres régions."

    print(f"Question : {question}")
    print(f"Réponse AICHA : {reponse}")
    print("\nIBRAHIMA évalue...\n")

    evaluation = ibrahima_evaluate(question, reponse)
    print(f"Score : {evaluation['score']}/10")
    print(f"Valide : {evaluation['valide']}")
    print(f"Commentaire : {evaluation['commentaire']}")
    if evaluation.get('suggestion'):
        print(f"Suggestion : {evaluation['suggestion']}")