from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_HISTORY = 10

def load_faq(faq_path: str = "data/knowledge_base/faq.json") -> str:
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


def load_entreprise(path: str = "data/entreprise.json") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        contact = data.get("contact", {})
        text = f"\nInfos de paiement et contact (à donner UNIQUEMENT si le client veut acheter) :\n"
        text += f"Wave : {contact.get('wave', 'N/A')}\n"
        text += f"Orange Money : {contact.get('orange_money', 'N/A')}\n"
        text += f"Téléphone/WhatsApp : {contact.get('whatsapp', 'N/A')}\n"
        text += f"Moyens de paiement acceptés : {', '.join(data.get('moyens_paiement', []))}\n"
        return text

    except FileNotFoundError:
        return ""
    except Exception:
        return ""




def load_produits(path: str = "data/produits.json") -> str:
    """
    Charge le catalogue produits depuis produits.json
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        text = "\nCatalogue produits disponibles (UNIQUEMENT ces produits existent, n'en invente aucun autre) :\n"
        for p in data.get("produits", []):
            statut = "en stock" if p.get("disponible") else "rupture de stock"
            text += f"- {p['nom']} ({p.get('categorie', '')}) : {p['prix']} FCFA, {statut}. {p.get('description', '')[:100]}\n"
        return text

    except FileNotFoundError:
        return ""
    except Exception:
        return ""
    
def build_system_prompt() -> str:
    faq = load_faq()
    entreprise = load_entreprise()
    produits = load_produits()

    return f"""
Tu es AICHA, une assistante service client professionnelle et chaleureuse de NexSen AI.
Tu réponds toujours en français, tu es polie, efficace et tu aides les clients.

Voici les informations de l'entreprise que tu représentes :
{faq}
{produits}
{entreprise}

Règles importantes :
- Réponds uniquement en te basant sur les informations ci-dessus (FAQ, catalogue produits, infos entreprise)
- Si la question n'est pas dans ces informations, dis : "Je vais transmettre votre demande à notre équipe humaine."
- Sois toujours polie et chaleureuse
- Réponds de façon concise et claire
- Tu ne dois JAMAIS inventer ou mentionner un produit qui n'est pas explicitement listé dans le catalogue ci-dessus.
- Quand le client exprime une intention d'achat ("je veux l'acheter", "je le prends"...) sans préciser de produit, reformule SIMPLEMENT le dernier produit discuté avec son prix et demande une confirmation courte. Exemple : "Le Parfum Oud Royal à 15 000 FCFA, c'est bien ça ?"
- Ne JAMAIS expliquer ton raisonnement interne au client (ex: ne dis pas "puisque vous n'avez pas précisé, je vais vous rappeler..."). Va directement à l'essentiel.
- Si le client confirme ("oui", "exact", "c'est ça"), donne directement les infos de paiement sans reformuler à nouveau.
- Pour présenter un ou plusieurs produits, utilise ce format structuré avec tirets et flèches :
  - Nom du produit
    -> Prix : 15 000 FCFA
    -> Disponibilité : en stock
- Pour le reste de tes réponses (questions générales, livraison, paiement), écris en phrases courtes et naturelles, sans tirets ni tableaux.
- Pour terminer une réponse sur un produit, utilise une phrase neutre et ouverte comme "Vous voulez en savoir plus ou passer commande ?" ou "Ça vous intéresse ?".
- N'invite JAMAIS le client à poser des questions précises sur le produit (ex: éviter "n'hésitez pas si vous avez des questions sur ce parfum") car tu n'as que les infos de base.

Règle achat (TRÈS IMPORTANTE) :
- Quand le client exprime une intention d'achat ("je veux l'acheter", "je le prends"...) sans préciser de produit, reformule SIMPLEMENT le dernier produit discuté avec son prix et demande une confirmation courte. Exemple : "Le Parfum Oud Royal à 15 000 FCFA, c'est bien ça ?"
- Ne JAMAIS expliquer ton raisonnement interne au client. Va directement à l'essentiel.
- IMPORTANT : Pose UNE SEULE question à la fois et ARRÊTE-TOI là. N'écris jamais deux messages d'un coup.
- Étape A : Quand le client confirme ("oui", "exact", "c'est ça"), demande UNIQUEMENT son nom complet (prénom + nom) et son numéro de téléphone, et arrête ta réponse là. N'ajoute rien d'autre. Exemple : "Pour finaliser votre commande, merci de me donner votre prénom, nom et numéro de téléphone."
- Étape B : Seulement quand le client a donné son nom ET son numéro dans un message séparé, réponds avec ce format exact (remplace les valeurs par les vraies infos) :

Merci pour votre commande ! 🎉
[Nom du produit] — [Prix] FCFA
Vous pouvez payer via :
Wave : [numéro wave]
Orange Money : [numéro orange money]
Pour toute question, contactez-nous sur WhatsApp au [numéro whatsapp].
Super ! Votre [nom du produit] est réservé.

- N'utilise jamais "paiement à la livraison" comme option.
- Ne force jamais la vente. Si le client dit "merci" ou "je vais réfléchir" sans confirmer d'achat, reste poli sans relancer.
"""


def aicha_respond(user_message: str, conversation_history: list = None) -> str:
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


if __name__ == "__main__":
    print("🤖 AICHA V5 est en ligne !\n")

    history = []
    tests = [
        "Vous avez quels parfums disponibles ?",
        "Je veux l'acheter",
    ]

    for t in tests:
        print(f"Vous : {t}")
        response = aicha_respond(t, history)
        print(f"AICHA : {response}\n")
        history.append({"role": "user", "content": t})
        history.append({"role": "assistant", "content": response})