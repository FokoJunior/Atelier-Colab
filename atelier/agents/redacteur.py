"""Agent Redacteur : ecrit l'article Markdown source a partir du plan et du dossier."""

from google.adk.agents import Agent

from atelier.agents.commun import REGLE


def creer_redacteur(modele):
    return Agent(
        name="Redacteur",
        model=modele,
        instruction=REGLE
        + "Redige un article francais original en Markdown, environ "
        "900 a 1400 mots si le dossier le permet. "
        "Inclue un titre H1, une introduction et des sections H2. "
        "Cite les affirmations factuelles avec [S1], [S2], etc., "
        "en utilisant exclusivement les identifiants associes aux preuves. "
        "Ne cree ni URL ni bibliographie : le programme les ajoutera. "
        "Distingue les faits des conseils et des inferences. "
        "Pas de HTML, d'images, de citations longues ni de cloture de code "
        "autour de l'article entier. Tiens compte des corrections eventuelles.",
    )
