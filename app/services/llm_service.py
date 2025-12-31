import json
import abc
from openai import AsyncOpenAI
from google import genai
from google.genai import types
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging_config import app_logger, error_logger


class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def analyze(self, subject_code: str, history: list) -> dict:
        pass

    def _build_prompt(self, subject_code: str, history: list) -> str:
        return f"""
        You are an academic risk analysis engine.
        
        TASK:
        Analyze the student's readiness for the target subject using ONLY the provided academic history.
        
        TARGET SUBJECT: {subject_code}
        STUDENT ACADEMIC HISTORY: {history}
        
        OUTPUT RULES:
        - Return ONLY valid JSON.
        - JSON Structure:
        {{
          "subject_code": "{subject_code}",
          "risk_level": "Low | Medium | High",
          "key_signals": [{{"signal": "...", "description": "..."}}],
          "risk_drivers": ["..."],
          "recommended_focus": ["..."]
        }}
        """

class GeminiProvider(LLMProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    async def analyze(self, subject_code: str, history: list) -> dict:
        prompt = self._build_prompt(subject_code, history)
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            return json.loads(response.text)

        except Exception as e:
            error_logger.error(f"Gemini (New SDK) Error: {e}")
            raise HTTPException(status_code=502, detail="AI provider failed")


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str, model_name: str):
        if not api_key:
            raise ValueError("API Key missing for OpenAI/DeepSeek provider")
        
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    async def analyze(self, subject_code: str, history: list) -> dict:
        prompt = self._build_prompt(subject_code, history)
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful JSON API."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            error_logger.error(f"OpenAI/DeepSeek Error: {e}")
            raise HTTPException(status_code=502, detail="AI provider failed")


def get_llm_provider(provider_name: str = None) -> LLMProvider:
    provider_name = provider_name
    provider_name = provider_name.lower()

    app_logger.info(f"Initializing LLM Provider: {provider_name}")

    if provider_name == "gemini":
        return GeminiProvider()
    
    elif provider_name == "openai":
        return OpenAICompatibleProvider(
            api_key=settings.OPENAI_API_KEY,
            base_url="https://api.openai.com/v1",
            model_name=settings.OPENAI_MODEL
        )
        
    elif provider_name == "deepseek":
        return OpenAICompatibleProvider(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
            model_name=settings.DEEPSEEK_MODEL
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider_name}")