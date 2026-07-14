"""
LLM summarization using OpenRouter API (OpenAI-compatible endpoint).
"""
import json
import re
import logging
# pyrefly: ignore [missing-import]
from openai import AsyncOpenAI
from config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

# Shared client - reused across requests for performance
client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

_SYSTEM_PROMPT = (
    "You are an expert meeting analyst. Read the transcript and return ONLY a valid JSON object with this structure:\n"
    "{\n"
    "  \"summary\": \"string (3-5 sentences)\",\n"
    "  \"decisions\": [\"string\"],\n"
    "  \"action_items\": [{\"task\": \"string\", \"owner\": \"string\", \"deadline\": \"string\", \"priority\": \"string\"}]\n"
    "}\n"
    "Use 'Unassigned' if owner not mentioned. Use 'Not specified' if deadline not mentioned.\n"
    "Priority must be High, Medium, or Low.\n"
    "Return ONLY the JSON object — no markdown, no explanation, no extra text."
)


def _extract_json(text: str) -> dict:
    """Strip markdown code fences and parse JSON from the model response."""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```\s*$", "", text.strip())
    return json.loads(text.strip())


async def summarize_transcript(transcript: str) -> dict:
    """
    Calls an OpenRouter-hosted LLM to summarize the transcript and extract action items.
    Returns a dict with keys: summary, decisions, action_items.
    """
    try:
        response = await client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            max_tokens=1024,
        )

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError("Model returned empty response")

        logger.debug(f"Raw AI response: {content[:300]}")
        return _extract_json(content)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return {"summary": "Failed to parse summary from AI response.", "decisions": [], "action_items": []}
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise
