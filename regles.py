# regles.py
# C'est ici que tu definis a qui chaque email est transfere.
# Tu peux modifier ce fichier sans toucher a la logique principale dans app.py


# --- REGLES PAR MOT-CLE (PRIORITAIRES) ---
# Chaque ligne = un mot-cle (en minuscules) -> une liste de destinataires.
# Si ce mot-cle apparait dans le sujet ou le corps de l'email,
# l'email est transfere a la (ou les) adresse(s) correspondante(s).
# Ces regles sont verifiees EN PREMIER.
#
# Tu peux ajouter, modifier ou supprimer des lignes librement.
# Exemple :
#   "aibd": ["personne1@projet.courses"],
#   "eamac": ["personne2@projet.courses"],
#   "asecna": ["personne3@projet.courses"],
#   "urgent": ["personne4@projet.courses"],

REGLES_CONTENU = {
    "aibd": ["ondoarsenico@gmail.com"],
    "eamac": ["mangaeerr@gmail.com"],
    "asecna": ["ndongarsenico@gmail.com"],
    "urgent": ["maouhedj@gmail.com"],
}


# --- REGLES PAR EXPEDITEUR (optionnel, verifiees APRES les mots-cles) ---
# Si tu veux qu'un expediteur precis declenche un transfert quand
# aucun mot-cle n'a correspondu, ajoute-le ici.
# Exemple :
#   "client1@exemple.com": ["personne1@projet.courses"],

REGLES_EXPEDITEUR = {
    
}


def choisir_destinataires(expediteur: str, sujet: str, corps: str) -> list[str] | None:
    """Decide a qui transferer un email selon les mots-cles dans le sujet.

    Renvoie None si aucune regle ne correspond, ce qui signifie que
    l'email ne doit PAS etre transfere.
    """

    # On cherche TOUS les mots-cles dans le sujet uniquement
    sujet_lower = sujet.lower()
    tous_destinataires = []

    for mot, destinataires in REGLES_CONTENU.items():
        if mot in sujet_lower:
            for d in destinataires:
                if d not in tous_destinataires:  # eviter les doublons
                    tous_destinataires.append(d)

    # Si au moins un mot-cle a correspondu, on renvoie tous les destinataires trouves
    if tous_destinataires:
        return tous_destinataires

    # Sinon, on regarde si l'expediteur exact a une regle
    if expediteur in REGLES_EXPEDITEUR:
        return REGLES_EXPEDITEUR[expediteur]

    # Aucune regle ne correspond : pas de transfert
    return None


