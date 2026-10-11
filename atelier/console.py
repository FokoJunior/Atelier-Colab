"""Mise en forme de l'affichage console (sections, sources, URLs tronquees, Markdown simplifie)."""

import re
import shutil

LARGEUR = min(shutil.get_terminal_size(fallback=(100, 24)).columns, 100)


def formater_markdown(texte):
    """Rend un Markdown simple plus lisible dans un terminal brut (sans dependance externe).
    Les fichiers exportes (.md, .html) conservent le Markdown original intact."""
    lignes = []
    for ligne in texte.splitlines():
        brute = ligne.strip()
        if brute.startswith("### "):
            lignes.append("  " + brute[4:].upper())
        elif brute.startswith("## "):
            lignes.append(brute[3:].upper())
        elif brute.startswith("# "):
            lignes.append(brute[2:].upper())
        elif brute.startswith(("- ", "* ")):
            lignes.append("  • " + re.sub(r"\*\*(.+?)\*\*", r"\1", brute[2:]))
        else:
            lignes.append(re.sub(r"\*\*(.+?)\*\*", r"\1", ligne))
    return "\n".join(lignes)


def titre(texte):
    print("\n" + "=" * LARGEUR)
    print(texte)
    print("=" * LARGEUR)


def tronquer(texte, longueur):
    return texte if len(texte) <= longueur else texte[: longueur - 1] + "…"


def afficher_sources(sources):
    print(f"Sources etayees : {len(sources)}\n")
    for s in sources:
        print(f"  [{s['id']}] {tronquer(s['titre'], 28):<28}  {tronquer(s['url'], 55)}")
    print("\n  (URLs completes dans sources.json et dossier_recherche.json)")


def afficher_requetes(requetes):
    print("Requetes reellement envoyees a Google :")
    for q in requetes:
        print(f"  - {q}")


def resume_final(statut, corrections, sortie, archive):
    titre("Resultat")
    marque = "✔" if statut == "CONTROLES_AUTOMATIQUES_PASSES" else "⚠"
    print(f"  {marque} Statut : {statut}")
    if corrections:
        print("  Corrections restant a traiter :")
        for c in corrections:
            print(f"    - {c}")
    print(f"  Dossier  : {sortie}")
    print(f"  Archive  : {archive}")
