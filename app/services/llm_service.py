import json
import abc
import re
from google import genai
from google.genai import types
from openai import AsyncOpenAI
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging_config import app_logger, error_logger

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def analyze(self, target_paper: dict, history: list) -> dict:
        pass

    def _clean_json_response(self, raw_text: str) -> dict:
        """
        Production Fix: Strips Markdown code blocks (e.g. ```json ... ```)
        and attempts to locate the valid JSON object.
        """
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            clean_text = re.sub(r"```json\s*|\s*```", "", raw_text).strip()
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError:
                match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(1))
                    except:
                        pass
                
                error_logger.error(f"Failed to parse JSON. Raw: {raw_text[:100]}...")
                return None

    def _build_prompt(self, target_paper: dict, history: list) -> str:
        
        predict_context = f"predict paper name: {target_paper.get('PaperName', 'Unknown')} ({target_paper.get('PaperCode', 'Unknown')})"
        
        dep_lines = []
        deps = target_paper.get('DependencyCourseData', [])
        if deps:
            for dep in deps:
                dep_lines.append(
                    f"dependency paper name: {dep.get('DependencyCourseName', 'Unknown')} | "
                    f"Weightage: {dep.get('Weightage', 'N/A')} out of 5 | "
                    f"Reason: {dep.get('Reason', 'N/A')}"
                )
        else:
            dep_lines.append("dependency paper name: None")
        
        dependency_context = "\n".join(dep_lines)
        
        history_lines = []
        for h in history:
            int_mark = h.get('InternalMark', 0)
            int_max = h.get('InternalMaxMark', 0)
            ext_mark = h.get('ExternalMark', 0)
            ext_max = h.get('ExternalMaxMark', 0)
            
            int_display = f"{int_mark}/{int_max}" if int_max else "null"
            ext_display = f"{ext_mark}/{ext_max}" if ext_max else "null"
            
            line = (
                f"exam details: {h.get('PaperName', 'Unknown')} ({h.get('PaperCode', 'Unknown')}) : "
                f"internal: {int_display}, external: {ext_display}"
            )
            history_lines.append(line)
        
        history_context = "\n".join(history_lines)

        prompt = f"""
        You are an academic risk analyzer.
        
        CONTEXT FORMAT:
        {predict_context}
        {dependency_context}
        
        STUDENT HISTORY:
        {history_context}
        
        TASK:
        Analyze the risk for the 'predict paper name' based on the dependencies and exam history.
        
        OUTPUT RULES:
        - Return ONLY valid JSON.
        - JSON Structure:
        {{
          "paper_name": "{target_paper.get('PaperName', '')}",
          "paper_code": "{target_paper.get('PaperCode', '')}",
          "risk_level": "High | Medium | Low",
          "key_signals": [{{"signal": "Short Title", "description": "Explanation"}}],
          "risk_drivers": ["Point 1", "Point 2"],
          "recommended_focus": ["Action 1", "Action 2"]
        }}
        """
        return prompt

class GeminiProvider(LLMProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    async def analyze(self, target_paper: dict, history: list) -> dict:
        prompt = self._build_prompt(target_paper, history)
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            result = self._clean_json_response(response.text)
            if not result:
                raise ValueError("JSON parsing failed")
            return result

        except Exception as e:
            error_logger.error(f"Gemini Error for {target_paper.get('PaperCode')}: {e}")
            return self._get_fallback_response(target_paper)

    def _get_fallback_response(self, target_paper):
        return {
            "paper_name": target_paper.get('PaperName'),
            "paper_code": target_paper.get('PaperCode'),
            "risk_level": "Unknown",
            "key_signals": [{"signal": "Error", "description": "Analysis Failed"}],
            "risk_drivers": [],
            "recommended_focus": []
        }

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    async def analyze(self, target_paper: dict, history: list) -> dict:
        prompt = self._build_prompt(target_paper, history)
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a JSON-only API."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            error_logger.error(f"AI Provider Error: {e}")
            return {
                "paper_name": target_paper.get('PaperName'),
                "paper_code": target_paper.get('PaperCode'),
                "risk_level": "Unknown",
                "key_signals": [],
                "risk_drivers": [],
                "recommended_focus": []
            }

def get_llm_provider(provider_name: str = None) -> LLMProvider:
    provider_name = provider_name or "gemini"
    
    app_logger.debug(f"Initializing Provider: {provider_name}")

    if provider_name == "gemini":
        return GeminiProvider()
    elif provider_name == "openai":
        return OpenAICompatibleProvider(
            settings.OPENAI_API_KEY, 
            "[https://api.openai.com/v1](https://api.openai.com/v1)", 
            settings.OPENAI_MODEL
        )
    elif provider_name == "deepseek":
        return OpenAICompatibleProvider(
            settings.DEEPSEEK_API_KEY, 
            "[https://api.deepseek.com/v1](https://api.deepseek.com/v1)", 
            settings.DEEPSEEK_MODEL
        )
    else:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider_name}")   