# Reenvio automatico de correos

Cette application surveille ta boite Gmail, et reenvoie automatiquement
les nouveaux emails vers des destinataires choisis selon des regles
(expediteur ou contenu), en utilisant l'API de Resend.

## 1. Installer les dependances

Assure-toi d'avoir Python installe, puis dans le dossier du projet :

```bash
pip install -r requirements.txt
```

## 2. Activer la verification en deux etapes sur Google

Va sur https://myaccount.google.com/security et active
"Verification en deux etapes" si ce n'est pas deja fait.
C'est obligatoire pour pouvoir generer un mot de passe d'application.

## 3. Generer un "mot de passe d'application" Gmail

1. Toujours sur https://myaccount.google.com/security
2. Cherche "Mots de passe des applications" (App passwords)
3. Cree-en un nouveau (nom libre, ex: "reenvio-app")
4. Google te donne un code de 16 caracteres -> copie-le

Ce code va dans `GMAIL_APP_PASSWORD` (jamais ton mot de passe Gmail normal).

## 4. Configurer un domaine sur Resend

1. Cree un compte sur https://resend.com
2. Va dans "Domains" et ajoute un domaine que tu possedes
3. Resend te donne des enregistrements DNS (TXT, MX, etc.) a ajouter
   chez ton fournisseur de domaine (Namecheap, Cloudflare, etc.)
4. Attends que le domaine soit verifie (peut prendre de quelques minutes
   a quelques heures)
5. Recupere ta cle API dans "API Keys" -> va dans `RESEND_API_KEY`

L'adresse `FROM_EMAIL` (ex: reenvios@tondomaine.com) doit utiliser
ce domaine verifie.

## 5. Creer le fichier .env

Copie `.env.example` vers `.env` :

```bash
cp .env.example .env
```

Puis remplis `.env` avec tes vraies valeurs (Gmail, mot de passe
d'application, cle Resend, domaine).

## 6. Personnaliser les regles de reenvoi

Ouvre `reglas.py` et modifie :
- `REGLAS_REMITENTE` : reenvoi base sur l'adresse de l'expediteur
- `REGLAS_CONTENIDO` : reenvoi base sur des mots-cles dans le sujet/corps
- `DESTINATARIO_DEFAULT` : ou envoyer si aucune regle ne correspond

## 7. Lancer l'application

```bash
python app.py
```

Elle va verifier ta boite toutes les 60 secondes (configurable via
`INTERVALO_SEGUNDOS` dans `.env`) et reenvoyer les nouveaux emails
selon tes regles.

## 8. Deploiement (pour que ca tourne 24/7)

Pour que ca fonctionne en continu sans laisser ton ordinateur allume,
deploie ce projet sur un service comme Render ou Railway (plan gratuit
disponible pour des projets simples). Configure les memes variables
d'environnement (.env) dans les parametres du service.
