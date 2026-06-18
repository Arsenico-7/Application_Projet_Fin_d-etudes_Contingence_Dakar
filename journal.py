# journal.py
# Ce module enregistre l'historique des emails transferes dans une base
# SQLite locale (un simple fichier "journal.db"), pour pouvoir l'afficher
# ensuite sur le dashboard web.

import sqlite3
from datetime import datetime

NOM_BASE = "journal.db"


def initialiser():
    """Cree la table si elle n'existe pas encore. A appeler au demarrage."""
    connexion = sqlite3.connect(NOM_BASE)
    connexion.execute("""
        CREATE TABLE IF NOT EXISTS transferts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_heure TEXT NOT NULL,
            expediteur TEXT NOT NULL,
            sujet TEXT,
            destinataires TEXT NOT NULL
        )
    """)
    connexion.commit()
    connexion.close()


def enregistrer(expediteur: str, sujet: str, destinataires: list[str]):
    """Ajoute une ligne dans le journal pour un email qui vient d'etre transfere."""
    connexion = sqlite3.connect(NOM_BASE)
    connexion.execute(
        "INSERT INTO transferts (date_heure, expediteur, sujet, destinataires) VALUES (?, ?, ?, ?)",
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            expediteur,
            sujet,
            ", ".join(destinataires),
        ),
    )
    connexion.commit()
    connexion.close()


def lister_derniers(limite: int = 50):
    """Renvoie les derniers transferts, du plus recent au plus ancien."""
    connexion = sqlite3.connect(NOM_BASE)
    curseur = connexion.execute(
        "SELECT date_heure, expediteur, sujet, destinataires "
        "FROM transferts ORDER BY id DESC LIMIT ?",
        (limite,),
    )
    lignes = curseur.fetchall()
    connexion.close()
    return lignes
