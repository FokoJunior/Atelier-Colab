"""Configuration et chargement de la cle API."""

import os

from dotenv import load_dotenv

MIN_SOURCES = 3
MAX_VERSIONS = 2


def charger_cle_api():
    load_dotenv()
    cle = os.environ.get("GOOGLE_API_KEY")
    if not cle or not cle.strip():
        cle = input("Cle Gemini API (visible dans ce terminal) : ")
    if not cle or not cle.strip():
        raise ValueError("Une cle API reelle est necessaire.")
    os.environ["GOOGLE_API_KEY"] = cle.strip()
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
    return cle.strip()
