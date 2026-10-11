"""Controle automatique des references dans l'article redige."""

import re

from atelier.config import MIN_SOURCES


def controler_references(texte, sources):
    autorises = {s["id"] for s in sources}
    cites = set(re.findall(r"\[(S\d+)\]", texte))
    problemes = []
    if not texte.lstrip().startswith("# ") or "\n## " not in texte:
        problemes.append("Ajouter un titre H1 et des sections H2.")
    if len(cites) < MIN_SOURCES:
        problemes.append("Utiliser au moins trois identifiants du dossier.")
    if cites - autorises:
        problemes.append("Supprimer ces references inconnues : " + str(sorted(cites - autorises)))
    if re.search(r"https?://|www\.|<[^>]+>", texte):
        problemes.append("Retirer URL et HTML : les liens sont ajoutes par le programme.")
    if "![" in texte:
        problemes.append("Retirer les images du texte genere.")
    return problemes
