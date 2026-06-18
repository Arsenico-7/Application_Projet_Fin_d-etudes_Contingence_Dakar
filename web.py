# web.py
# Application web (dashboard) qui affiche :
#  - le journal des emails transferes (page d'accueil)
#  - les regles de transfert actuellement configurees
#
# A lancer avec : uvicorn web:app --reload
# Puis ouvrir http://127.0.0.1:8000 dans le navigateur.
#
# Ce fichier ne fait QUE de l'affichage. La logique de transfert
# (lecture Gmail, envoi via Resend) reste dans app.py, qui doit
# tourner separement.

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

import journal
import regles

app = FastAPI()

# Dossier pour les images et fichiers statiques (logos, etc.)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# On s'assure que la base de donnees existe, meme si app.py n'a pas
# encore tourne (sinon la page d'accueil planterait).
journal.initialiser()


@app.get("/", response_class=HTMLResponse)
def page_accueil(request: Request):
    transferts = journal.lister_derniers(50)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"transferts": transferts},
    )


@app.get("/principe", response_class=HTMLResponse)
def page_principe(request: Request):
    return templates.TemplateResponse(request, "principe.html", {})


@app.get("/apropos", response_class=HTMLResponse)
def page_apropos(request: Request):
    return templates.TemplateResponse(request, "apropos.html", {})


@app.get("/regles", response_class=HTMLResponse)
def page_regles(request: Request):
    return templates.TemplateResponse(
        request,
        "regles.html",
        {
            "regles_expediteur": regles.REGLES_EXPEDITEUR,
            "regles_contenu": regles.REGLES_CONTENU,
        },
    )
