import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()

def extraire_telephone(texte: str) -> str:
    texte_clean = re.sub(r'[\s\-\.]', '', texte)
    patterns = [
        r'\+221(7[0-8]\d{7})',
        r'00221(7[0-8]\d{7})',
        r'(7[0-8]\d{7})',
    ]
    for pattern in patterns:
        match = re.search(pattern, texte_clean)
        if match:
            numero = match.group(1)
            return f"{numero[:2]} {numero[2:5]} {numero[5:7]} {numero[7:9]}"
    return "Non fourni"

def extraire_nom(message: str) -> str:
    texte = message
    texte = re.sub(r'\+?2?2?1?\s?[\s\-\.]?(7[0-8])[\s\-\.]?\d{3}[\s\-\.]?\d{2}[\s\-\.]?\d{2}', '', texte)
    texte = re.sub(r'[,;\-]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte).strip()
    return texte if texte else "Non fourni"

def extraire_infos_commande(history: list, message_client: str) -> dict:
    texte_complet = " ".join([m.get("content", "") for m in history]) + " " + message_client

    telephone = extraire_telephone(message_client)
    nom = extraire_nom(message_client)

    produit = "Non identifié"
    prix = "Non identifié"
    produit_id = None

    try:
        with open("data/produits.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for p in data.get("produits", []):
            if p["nom"].lower() in texte_complet.lower():
                produit = p["nom"]
                prix = f"{p['prix']} FCFA"
                produit_id = p["id"]
                break
    except Exception:
        pass

    return {
        "nom": nom,
        "telephone": telephone,
        "produit": produit,
        "prix": prix,
        "produit_id": produit_id
    }


def update_stock(produit_id: str, quantite: int = 1) -> bool:
    try:
        with open("data/produits.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for p in data.get("produits", []):
            if p["id"] == produit_id:
                nouveau_stock = max(0, p["stock"] - quantite)
                p["stock"] = nouveau_stock
                if nouveau_stock == 0:
                    p["disponible"] = False
                    print(f"⚠️ {p['nom']} est maintenant en rupture de stock !")
                else:
                    print(f"✅ Stock mis à jour : {p['nom']} → {nouveau_stock} unités restantes")
                break

        with open("data/produits.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True

    except Exception as e:
        print(f"⚠️ Erreur mise à jour stock : {str(e)}")
        return False


def envoyer_notification_achat(history: list, message_client: str, reponse_aicha: str) -> bool:
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    if not all([sender, password, receiver]):
        print("⚠️ Configuration email incomplète dans .env")
        return False

    infos = extraire_infos_commande(history, message_client)

    if infos["produit_id"]:
        update_stock(infos["produit_id"])

    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = "🔔 NexSen AI - Nouvelle commande !"

        body = f"""
Nouvelle commande reçue !

Client : {infos['nom']}
Téléphone : {infos['telephone']}
Produit : {infos['produit']}
Prix : {infos['prix']}

---
NexSen AI 🌍
"""
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        print("✅ Notification envoyée avec succès")
        return True

    except Exception as e:
        print(f"⚠️ Erreur envoi notification : {str(e)}")
        return False


def detecter_intention_achat(message_client: str, reponse_aicha: str) -> bool:
    reponse_lower = reponse_aicha.lower()
    return "est réservé" in reponse_lower and "wave" in reponse_lower