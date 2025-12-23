import json
import google.generativeai as genai
from fastapi import HTTPException

from app.core.config import settings
from app.core.logging_config import app_logger, error_logger

genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

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

TASK:
Analyze the student's readiness for the target subject using ONLY the provided academic history.
Focus on weaknesses, gaps, and performance trends that may impact success.

TARGET SUBJECT:
{subject_code}

STUDENT ACADEMIC HISTORY (prerequisite subjects only):
{filtered_history}

ANALYSIS GUIDELINES:
- Evaluate internal, external, and overall performance.
- Identify conceptual weaknesses, not just low scores.
- Consider consistency across assessments.
- Do NOT summarize strengths unless relevant to risk.

RISK LEVEL RULES:
- Low: Strong and consistent performance with no major gaps.
- Medium: Mixed performance or minor conceptual weaknesses.
- High: Poor performance or clear foundational gaps.

OUTPUT RULES:
- Return ONLY valid JSON.
- Be specific and concise.
- Avoid generic advice.
- Base every conclusion on the given data.

REQUIRED OUTPUT FORMAT:
{{
  "subject_code": "string",
  "risk_level": "Low | Medium | High",
  "key_signals": [
    {{
      "signal": "short risk indicator",
      "description": "clear explanation based on student data"
    }}
  ],
  "risk_drivers": [
    "specific factor contributing to risk"
  ],
  "recommended_focus": [
    "actionable study or skill improvement suggestion"
  ]
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
