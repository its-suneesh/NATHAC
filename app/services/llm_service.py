import json
import google.generativeai as genai
from fastapi import HTTPException
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

_executor = ThreadPoolExecutor(max_workers=2)


def _call_gemini(prompt: str):
    return gemini_model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )


def analyze_with_ai(subject_code: str, filtered_history: list) -> dict:
    prompt = f"""
You are an academic analysis engine.

Target Subject: {subject_code}
Student History: {filtered_history}

Return ONLY valid JSON:
{{
  "subject_code": "string",
  "risk_level": "Low | Medium | High",
  "key_signals": [
    {{ "signal": "string", "description": "string" }}
  ],
  "risk_drivers": ["string"],
  "recommended_focus": ["string"]
}}
"""

    future = _executor.submit(_call_gemini, prompt)

    try:
        response = future.result(timeout=20)  # 🔥 HARD TIMEOUT
        return json.loads(response.text)

    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="AI analysis timed out"
        )

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {e}"
        )
