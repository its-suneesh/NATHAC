import json
import google.generativeai as genai
from fastapi import HTTPException

from app.core.config import settings
from app.core.logging_config import app_logger, error_logger


# -------------------------------------------------
# Gemini configuration (STABLE & WORKING)
# -------------------------------------------------
genai.configure(api_key=settings.GEMINI_API_KEY)

# This model is confirmed working for your account
gemini_model = genai.GenerativeModel("gemini-2.5-flash")


# -------------------------------------------------
# Async AI analysis function (NON-BLOCKING)
# -------------------------------------------------
async def analyze_with_ai(subject_code: str, filtered_history: list) -> dict:
    """
    Calls Gemini AI asynchronously to analyze academic risk.
    This will NOT block FastAPI.
    """

    app_logger.info(
        f"LLM analysis started | Subject={subject_code} | HistorySize={len(filtered_history)}"
    )

    prompt = f"""
You are an academic risk analysis engine.

Target Subject: {subject_code}
Student History: {filtered_history}

Return ONLY valid JSON in the following format:
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

    try:
        response = await gemini_model.generate_content_async(
            prompt,
            generation_config={
                "response_mime_type": "application/json"
            }
        )

        app_logger.info(
            f"LLM analysis completed | Subject={subject_code}"
        )

        return json.loads(response.text)

    except Exception as e:
        error_logger.error(
            f"LLM analysis failed | Subject={subject_code} | Error={e}"
        )
        raise HTTPException(
            status_code=502,
            detail="AI analysis failed"
        )
