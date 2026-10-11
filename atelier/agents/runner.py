"""Execution d'un agent ADK dans une session dediee."""

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def appeler_agent(agent, contenu):
    service = InMemorySessionService()
    session = await service.create_session(app_name="atelier_colab", user_id="auteur")
    runner = Runner(agent=agent, app_name="atelier_colab", session_service=service)
    resultat = ""
    async for event in runner.run_async(
        user_id="auteur",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part.from_text(text=contenu)]),
    ):
        if event.error_code:
            raise RuntimeError(f"Echec de {agent.name} : {event.error_code}")
        if event.is_final_response() and event.content:
            resultat = "".join(p.text or "" for p in event.content.parts or [])
    if not resultat.strip():
        raise RuntimeError("Sortie vide pour " + agent.name)
    return resultat
