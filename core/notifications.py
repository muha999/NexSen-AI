import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()

def extraire_infos_commande(history: list, message_client: str) -> dict:
    """
    Extrait nom, téléphone et produit depuis l'historique de conversation
    """
    texte_complet = " ".join([m.get("content", "") for m in history]) + " " + message_client

    tel_pattern = r"(\+221\s?)?(7[0-8])\s?\d{3}\s?\d{2}\s?\d{2}"
    tel_match = re.search(tel_pattern, texte_complet)
    telephone = tel_match.group(0) if tel_match else "Non fourni"

    produit = "Non identifié"
    prix = "Non identifié"
    try:
        with open("data/produits.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for p in data.get("produits", []):
            if p["nom"].lower() in texte_complet.lower():
                produit = p["nom"]
                prix = f"{p['prix']} FCFA"
                break
    except Exception:
        pass

    nom = "Non fourni"
    if tel_match:
        nom_candidat = message_client.replace(tel_match.group(0), "").strip()
        nom_candidat = re.sub(r"[,.\-]", "", nom_candidat).strip()
        if nom_candidat:
            nom = nom_candidat

    return {
        "nom": nom,
        "telephone": telephone,
        "produit": produit,
        "prix": prix
    }


def envoyer_notification_achat(history: list, message_client: str, reponse_aicha: str) -> bool:
    """
    Envoie un email récapitulatif propre au boutiquier
    """
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    if not all([sender, password, receiver]):
        print("⚠️ Configuration email incomplète dans .env")
        return False

    infos = extraire_infos_commande(history, message_client)

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
    """
    Détecte si AICHA a donné le message final de réservation
    """
    reponse_lower = reponse_aicha.lower()
    return "est réservé" in reponse_lower and "wave" in reponse_lower