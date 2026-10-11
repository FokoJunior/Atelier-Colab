"""Agent Relecteur : controle l'article contre les preuves et rend un avis structure."""

from google.adk.agents import Agent

from atelier.agents.commun import REGLE, Avis


def creer_relecteur(modele):
    return Agent(
        name="Relecteur",
        model=modele,
        instruction=REGLE
        + "Verifie l'article contre les preuves : faits, chiffres, dates, "
        "association des identifiants aux affirmations, francais et structure. "
        "Refuse les extrapolations presentees comme etablies. "
        "Refuse un texte qui dit avoir teste ce qui n'a pas ete teste. "
        "Rends ton avis selon le schema demande.",
        output_schema=Avis,
    )
