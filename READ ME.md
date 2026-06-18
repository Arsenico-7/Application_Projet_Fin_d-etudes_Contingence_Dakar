# Plan de contingence - Centre COM Dakar
## Transfert automatique d'emails

Ce projet surveille une boite Gmail et transfere automatiquement les
nouveaux emails vers des destinataires choisis, selon des regles bas
ees sur des mots-cles (ou, en option, sur l'expediteur). Les emails
sont envoyes via l'API de Resend, en utilisant le domaine
**projet.courses**. Un tableau de bord web affiche l'historique des
transferts et les regles actives.


## 1. Vue d'ensemble du fonctionnement

1. Un email arrive dans la boite Gmail configuree (`GMAIL_USER`).
2. Le programme `app.py` se connecte a cette boite par IMAP toutes
   les `INTERVALLE_SECONDES` (60 secondes par defaut) et recupere
   les emails non lus.
3. Pour chaque email, `regles.py` decide s'il doit etre transfere,
   et a qui :
   - il cherche d'abord si un **mot-cle** (defini dans
     `REGLES_CONTENU`) apparait dans le sujet ou le corps de l'email
     (priorite la plus haute) ;
   - si aucun mot-cle ne correspond, il regarde si l'**expediteur**
     est dans `REGLES_EXPEDITEUR` ;
   - si rien ne correspond, l'email **n'est pas transfere** (un
     message est simplement affiche dans le terminal).
4. Si une regle correspond, l'email est renvoye via Resend, avec
   `[Transfere]` ajoute au sujet, depuis l'adresse `FROM_EMAIL`.
5. Chaque transfert reussi est enregistre dans `journal.db` (base
   SQLite locale).
6. Le tableau de bord web (`web.py`) affiche ce journal sur la page
   d'accueil, et les regles actives sur la page `/regles`.


## 2. Structure du projet

```
PROYECTO/
├── app.py              -> programme principal (lecture Gmail + envoi Resend)
├── web.py              -> tableau de bord web (FastAPI)
├── regles.py           -> regles de transfert (a personnaliser)
├── journal.py          -> gestion de l'historique (SQLite)
├── journal.db          -> base de donnees de l'historique (creee automatiquement)
├── requirements.txt    -> liste des librairies Python necessaires
├── .env                -> tes informations secretes (a creer, jamais a partager)
├── .env.example        -> modele du fichier .env
├── .gitignore          -> exclut .env et autres fichiers sensibles de Git
└── templates/
    ├── base.html        -> structure commune (titre, navigation, pied de page)
    ├── index.html        -> page "Journal" (historique des transferts)
    └── regles.html       -> page "Regles" (regles actives)
```


## 3. Installation (premiere fois sur une nouvelle machine)

### a) Verifier que Python est installe

Dans un terminal :

```bash
python --version
```

Si une erreur apparait (commande non reconnue), installe Python
depuis https://www.python.org/downloads/ en cochant bien la case
"Add Python to PATH" pendant l'installation.

### b) Installer les dependances

Dans le dossier du projet :

```bash
python -m pip install -r requirements.txt
```

### c) Creer le fichier .env

Copie `.env.example` vers `.env`, puis remplis-le avec tes vraies
informations (voir section 4 ci-dessous).


## 4. Variables du fichier .env

| Variable              | Description                                                                 |
|------------------------|------------------------------------------------------------------------------|
| `GMAIL_USER`           | Ton adresse Gmail complete (ex : `toncompte@gmail.com`)                     |
| `GMAIL_APP_PASSWORD`   | Mot de passe d'application Gmail (16 caracteres, sans espaces)               |
| `RESEND_API_KEY`       | Cle API recuperee dans le dashboard Resend (section "API Keys")              |
| `FROM_EMAIL`           | Adresse d'envoi, ex : `reenvios@projet.courses`                              |
| `INTERVALLE_SECONDES`  | A quelle frequence verifier les nouveaux emails (60 = chaque minute)         |

### Generer le mot de passe d'application Gmail

1. Active la verification en deux etapes :
   https://myaccount.google.com/security
2. Va sur https://myaccount.google.com/apppasswords
3. Cree un mot de passe d'application, copie immediatement le code
   de 16 caracteres (il ne s'affiche qu'une seule fois)
4. Colle ce code dans `.env`, **sans espaces**, sans guillemets

Si tu changes ce mot de passe plus tard, l'ancien devient invalide
et il faut mettre a jour `.env` avec le nouveau.


## 5. Personnaliser les regles de transfert (regles.py)

Toute la logique de "qui recoit quoi" est dans `regles.py`. C'est le
seul fichier que tu dois modifier au quotidien.

### Regles par mot-cle (prioritaires)

```python
REGLES_CONTENU = {
    "aibd": ["personne1@projet.courses"],
    "eamac": ["personne2@projet.courses"],
    "asecna": ["personne3@projet.courses"],
    "urgent": ["personne4@projet.courses"],
}
```

- Le mot-cle est recherche (en minuscules) dans le sujet **et** le
  corps de l'email.
- C'est une recherche de "sous-chaine" : le mot-cle "facture"
  correspond aussi a "facture impayee", mais aussi a "manufacture".
- Tu peux mettre plusieurs adresses pour un meme mot-cle :
  `"urgent": ["a@projet.courses", "b@projet.courses"]` (jusqu'a 50
  adresses par regle, limite de l'API Resend).

### Regles par expediteur (optionnel, verifiees apres les mots-cles)

```python
REGLES_EXPEDITEUR = {
    "client1@exemple.com": ["personne1@projet.courses"],
}
```

### Si aucune regle ne correspond

L'email n'est **pas transfere**. Un message s'affiche dans le
terminal de `app.py`, par exemple :

```
Aucune regle ne correspond pour l'email de xxx@exemple.com (sujet : "...") - email non transfere.
```

### Important apres modification

Apres avoir modifie et sauvegarde `regles.py`, **redemarre
`app.py`** (Ctrl+C puis `python app.py`) pour que les changements
soient pris en compte. Le tableau de bord (`web.py`, lance avec
`--reload`) se mettra a jour automatiquement sur la page `/regles`.


## 6. Lancer l'application

Il faut **deux terminaux ouverts en meme temps**, tous les deux dans
le dossier du projet :

**Terminal 1 - le programme de transfert :**

```bash
python app.py
```

Ce terminal affiche en continu ce qu'il se passe : connexion a
Gmail, emails trouves, transferts effectues ou ignores.

**Terminal 2 - le tableau de bord web :**

```bash
python -m uvicorn web:app --reload
```

Ouvre ensuite http://127.0.0.1:8000 dans le navigateur pour voir le
"Journal" des transferts et la page "Regles".

Si tu eteins ton PC, ces deux processus s'arretent. Au redemarrage,
il suffit de relancer les deux commandes ci-dessus (la configuration
et l'historique restent intacts).


## 7. Le domaine projet.courses et Resend

Le domaine `projet.courses` a ete achete sur Namecheap et verifie
sur Resend via 3 enregistrements DNS (TXT pour DKIM, MX + TXT pour
SPF, ajoutes dans Namecheap > Advanced DNS). Une fois le domaine
verifie, `FROM_EMAIL` peut etre n'importe quelle adresse se
terminant par `@projet.courses` (ex : `reenvios@projet.courses`),
**sans avoir besoin de creer cette boite mail au prealable** -
Resend l'utilise uniquement comme adresse d'envoi.

Limite a connaitre : un email peut etre envoye a un maximum de **50
destinataires** au total (champ "to" de l'API Resend).


## 8. Reinitialiser le journal (historique)

Pour repartir avec un historique vide :

1. Arrete `app.py` et `uvicorn` (Ctrl+C dans les deux terminaux)
2. Supprime le fichier `journal.db`
3. Relance `python app.py` puis `python -m uvicorn web:app --reload`
   - le fichier sera recree automatiquement, vide

Cela ne supprime que l'historique affiche dans le "Journal" - la
configuration (`.env`, `regles.py`) n'est pas affectee.


## 9. Aller plus loin (pistes futures)

- **Acceder au tableau de bord depuis le telephone / un autre PC sur
  le meme wifi** : lancer `python -m uvicorn web:app --host 0.0.0.0
  --reload`, puis utiliser l'adresse IP locale de la machine (ex :
  `http://192.168.1.50:8000`), visible avec `ipconfig`.
- **Deploiement permanent** (accessible depuis n'importe ou, sans
  garder le PC allume) : heberger le projet sur un service comme
  Render ou Railway, puis relier un sous-domaine (ex :
  `dashboard.projet.courses`) via un enregistrement CNAME dans
  Namecheap.
- **Modifier les regles depuis le navigateur** (au lieu d'editer
  `regles.py` a la main) : possible en ajoutant une page
  d'administration au tableau de bord.
