import json
import os
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def analyze_message(content: str):
    """Analyse un message Discord et retourne un score de risque."""
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "risk": 0,
            "reason": "OpenAI key missing"
        }

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": "Analyse un message Discord pour détecter spam, flood ou comportement suspect. Réponds uniquement en JSON avec risk (0-100) et reason."
            },
            {
                "role": "user",
                "content": content
            }
        ]
    )

    try:
        return json.loads(response.output_text)
    except Exception:
        return {
            "risk": 0,
            "reason": "invalid_ai_response"
        }
