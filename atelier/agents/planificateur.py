"""Agent Planificateur : produit le plan Markdown de l'article."""

from google.adk.agents import Agent

from atelier.agents.commun import REGLE


def creer_planificateur(modele):
    return Agent(
        name="Planificateur",
        model=modele,
        instruction=REGLE
        + "Elabore un plan en francais adapte au public et a l'angle. "
        "Chaque section doit indiquer les identifiants de sources utiles. "
        "Rends uniquement le plan Markdown.",
    )
