"""
Atelier "Recherche -> Article" - version locale (hors Google Colab).

Point d'entree CLI. La logique est repartie dans le package `atelier/` :
  - atelier/config.py       : constantes et cle API
  - atelier/recherche.py    : recherche Google reelle (etape 3)
  - atelier/agents/*.py     : un fichier par agent ADK (planificateur, redacteur, relecteur),
                              plus runner.py (execution) et controle.py (validation des references)
  - atelier/pipeline.py     : orchestration plan -> redaction -> relecture (etapes 4-5)
  - atelier/export.py       : export Markdown/HTML/JSON + archive ZIP (etape 6)

Usage :
    python atelier_agents.py --sujet "..." --public "..." --angle "..."
"""

import argparse
import asyncio
import os
import shutil
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from google import genai

from atelier.config import charger_cle_api
from atelier.export import exporter
from atelier.pipeline import construire_agents, planifier_rediger_corriger
from atelier.recherche import rechercher


async def executer(args):
    charger_cle_api()
    try:
        versions_installees = {p: version(p) for p in ["google-adk", "google-genai", "Markdown"]}
    except Exception:
        versions_installees = {}
    print("Configuration prete. Modele :", args.modele)
    print(versions_installees)

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    date = datetime.now(timezone.utc).date().isoformat()

    print("\n--- Etape 3 : recherche reelle ---")
    dossier = rechercher(client, args.sujet, args.public, args.angle, args.modele, date)
    print("Requetes reellement renvoyees :", dossier["requetes"])
    print("Sources etayees :", len(dossier["sources"]))
    for source in dossier["sources"]:
        print(source["id"], source["titre"], source["url"])

    print("\n--- Etape 4-5 : agents, redaction et correction ---")
    planificateur, redacteur, relecteur = construire_agents(args.modele)
    plan, article, statut, valide, corrections, historique = await planifier_rediger_corriger(
        planificateur, redacteur, relecteur, dossier, args.public, args.angle
    )

    print("\n--- Etape 6 : export ---")
    sortie, archive = exporter(args.sortie, dossier, plan, article, statut, valide, historique)

    if args.copier_vers:
        destination = Path(args.copier_vers)
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(archive, destination / archive.name)
        print("Archive egalement copiee dans :", destination)

    print("\nTermine. Dossier :", sortie, "| Archive :", archive)


def main():
    parser = argparse.ArgumentParser(description="Atelier Recherche -> Article (version locale)")
    parser.add_argument("--sujet", default="Comment utiliser les agents IA pour preparer une veille cybersecurite sourcee")
    parser.add_argument("--public", default="professionnels de la cybersecurite decouvrant les agents IA")
    parser.add_argument("--angle", default="methode pratique, limites et verification des informations")
    parser.add_argument("--modele", default="gemini-3.8-flash")
    parser.add_argument("--sortie", default="sorties", help="Dossier local ou creer article_<id>/ et l'archive zip")
    parser.add_argument("--copier-vers", default=None, help="Dossier local optionnel ou copier aussi l'archive (equivalent de l'etape Drive)")
    args = parser.parse_args()

    Path(args.sortie).mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(executer(args))
    except Exception as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
