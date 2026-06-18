# app.py
# Ceci est l'application principale.
# Elle fait ce qui suit, en boucle infinie :
#   1. Se connecte a ton compte Gmail par IMAP
#   2. Cherche les emails non lus
#   3. Pour chaque email, decide a qui le transferer (via regles.py)
#   4. Transfere cet email en utilisant l'API de Resend
#   5. Attend une minute et recommence

import imaplib
import email
import os
import time
from email.header import decode_header

import resend
from dotenv import load_dotenv

from regles import choisir_destinataires
import journal

# On charge les variables d'environnement depuis le fichier .env
load_dotenv()

# --- Configuration (vient du fichier .env, jamais ecrite en dur) ---
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]
FROM_EMAIL = os.environ["FROM_EMAIL"]  # doit etre d'un domaine verifie sur Resend
INTERVALLE_SECONDES = int(os.environ.get("INTERVALLE_SECONDES", "60"))

resend.api_key = RESEND_API_KEY


def decoder(valeur):
    """Convertit les en-tetes d'email (parfois encodes) en texte normal."""
    if valeur is None:
        return ""
    parties = decode_header(valeur)
    resultat = ""
    for texte, encodage in parties:
        if isinstance(texte, bytes):
            resultat += texte.decode(encodage or "utf-8", errors="ignore")
        else:
            resultat += texte
    return resultat


def extraire_corps(message):
    """Extrait le texte brut et le HTML de l'email, s'ils existent."""
    texte_brut = ""
    texte_html = ""

    if message.is_multipart():
        for partie in message.walk():
            type_partie = partie.get_content_type()
            disposition = str(partie.get("Content-Disposition") or "")

            if "attachment" in disposition:
                continue

            if type_partie == "text/plain" and not texte_brut:
                texte_brut = partie.get_payload(decode=True).decode(errors="ignore")
            elif type_partie == "text/html" and not texte_html:
                texte_html = partie.get_payload(decode=True).decode(errors="ignore")
    else:
        contenu = message.get_payload(decode=True).decode(errors="ignore")
        if message.get_content_type() == "text/html":
            texte_html = contenu
        else:
            texte_brut = contenu

    return texte_brut, texte_html


def traiter_nouveaux_emails():
    """Se connecte a Gmail, cherche les emails non lus et les transfere selon les regles."""

    print("Connexion a Gmail...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    mail.select("inbox")

    # On cherche uniquement les emails NON LUS (UNSEEN)
    _, donnees = mail.search(None, "UNSEEN")
    ids_emails = donnees[0].split()

    if not ids_emails:
        print("Aucun nouvel email.")
    else:
        print(f"{len(ids_emails)} nouvel/nouveaux email(s) trouve(s).")

    for id_email in ids_emails:
        _, donnees_message = mail.fetch(id_email, "(RFC822)")
        message = email.message_from_bytes(donnees_message[0][1])

        expediteur_complet = decoder(message.get("From"))
        # On extrait seulement l'adresse email, sans le nom
        expediteur = email.utils.parseaddr(expediteur_complet)[1]
        sujet = decoder(message.get("Subject"))

        texte_brut, texte_html = extraire_corps(message)

        destinataires = choisir_destinataires(expediteur, sujet, texte_brut or texte_html)

        if destinataires is None:
            print(
                f"Aucune regle ne correspond pour l'email de {expediteur} "
                f"(sujet : \"{sujet}\") - email non transfere."
            )
            continue

        print(f"Transfert de l'email de {expediteur} -> {destinataires}")

        corps_pour_transfert = texte_html or f"<pre>{texte_brut}</pre>"

        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": destinataires,
            "subject": f"[CAT de Dakar] {sujet}",
            "html": (
                f"<p><strong>De :</strong> {expediteur_complet}</p>"
                f"<hr>{corps_pour_transfert}"
            ),
        })

        journal.enregistrer(expediteur_complet, sujet, destinataires)

    mail.logout()


if __name__ == "__main__":
    print("Demarrage du service de transfert automatique d'emails...")
    journal.initialiser()
    while True:
        try:
            traiter_nouveaux_emails()
        except Exception as erreur:
            print(f"Erreur lors du traitement des emails : {erreur}")

        time.sleep(INTERVALLE_SECONDES)
