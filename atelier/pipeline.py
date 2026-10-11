"""Etapes 4-5 : construction des agents, puis plan / redaction / correction."""

import json

from atelier.agents.commun import Avis
from atelier.agents.controle import controler_references
from atelier.agents.planificateur import creer_planificateur
from atelier.agents.redacteur import creer_redacteur
from atelier.agents.relecteur import creer_relecteur
from atelier.agents.runner import appeler_agent
from atelier.config import MAX_VERSIONS


def construire_agents(modele):
    return creer_planificateur(modele), creer_redacteur(modele), creer_relecteur(modele)


async def planifier_rediger_corriger(planificateur, redacteur, relecteur, dossier, public, angle):
    preuves_agents = {k: v for k, v in dossier.items() if k != "suggestions_html"}
    contexte = json.dumps({"public": public, "angle": angle, "dossier": preuves_agents}, ensure_ascii=False)
    plan = await appeler_agent(planificateur, contexte)
    print("\n--- Plan ---\n" + plan)

    historique = []
    corrections = []
    valide = False
    article = ""
    for numero in range(1, MAX_VERSIONS + 1):
        print(f"Redaction et controle : version {numero}/{MAX_VERSIONS}")
        demande = json.dumps(
            {
                "contexte": preuves_agents,
                "public": public,
                "angle": angle,
                "plan": plan,
                "version_precedente": article if numero > 1 else "",
                "corrections": corrections,
            },
            ensure_ascii=False,
        )
        article = await appeler_agent(redacteur, demande)
        erreurs = controler_references(article, dossier["sources"])
        avis = Avis.model_validate_json(
            await appeler_agent(
                relecteur,
                json.dumps({"dossier": preuves_agents, "article": article, "public": public, "angle": angle}, ensure_ascii=False),
            )
        )
        corrections = erreurs + avis.corrections
        valide = avis.accepte and not corrections
        historique.append({"version": numero, "accepte": valide, "corrections": corrections, "article": article})
        if valide:
            break
    statut = "CONTROLES_AUTOMATIQUES_PASSES" if valide else "BROUILLON_A_REVOIR"
    print("Statut :", statut)
    if corrections:
        print("Corrections restant a traiter :", corrections)
    return plan, article, statut, valide, corrections, historique
