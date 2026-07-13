import json
import os
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def get_action(risk: int):
    if risk < 100:
        return "none"
    if risk < 200:
        return "warning"
    if risk < 300:
        return "mute"
    if risk >= 400:
        return "human_review"
    return "review"


async def analyze_message(content: str):
    """Analyse un message Discord et retourne un score de risque + action."""
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "risk": 0,
            "reason": "OpenAI key missing",
            "action": "none"
        }

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "Analyse un message Discord pour détecter spam, flood ou comportement suspect. "
                    "Retourne uniquement un JSON valide avec risk (0-400+), reason. "
                    "Plus le comportement est grave, plus le score doit être élevé."
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]
    )

    try:
        result = json.loads(response.output_text)
        risk = int(result.get("risk", 0))
        result["action"] = await get_action(risk)
        return result
    except Exception:
        return {
            "risk": 0,
            "reason": "invalid_ai_response",
            "action": "none"
        }
