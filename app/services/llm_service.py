import httpx
import openai
import google.generativeai as genai
from app.core.config import settings
from typing import Dict, Any, Optional

class LLMService:
    @staticmethod
    async def execute_prompt(
        model_provider: str, 
        model_name: str, 
        prompt_text: str, 
        config: Dict[str, Any] = {},
        provider_config: Dict[str, Any] = {}
    ) -> str:
        provider = model_provider.lower()
        if "openai" in provider:
            return await LLMService._run_openai(model_name, prompt_text, config, provider_config)
        elif "gemini" in provider:
            return await LLMService._run_gemini(model_name, prompt_text, config, provider_config)
        elif "ollama" in provider:
            return await LLMService._run_ollama(model_name, prompt_text, config, provider_config)
        else:
            raise ValueError(f"Unknown provider: {model_provider}")

    @staticmethod
    async def _run_openai(model: str, prompt: str, config: Dict[str, Any], provider_config: Dict[str, Any]) -> str:
        api_key = provider_config.get("api_key") or settings.OPENAI_API_KEY
        base_url = provider_config.get("base_url")
        if not api_key:
             raise ValueError("OpenAI API Key not set")
        
        client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.get("temperature", 0.7)
        )
        return response.choices[0].message.content

    @staticmethod
    async def _run_gemini(model: str, prompt: str, config: Dict[str, Any], provider_config: Dict[str, Any]) -> str:
        api_key = provider_config.get("api_key") or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("Gemini API Key not set")
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(model)
        response = await gemini_model.generate_content_async(prompt)
        return response.text

    @staticmethod
    async def _run_ollama(model: str, prompt: str, config: Dict[str, Any], provider_config: Dict[str, Any]) -> str:
        base_url = provider_config.get("base_url") or settings.OLLAMA_BASE_URL
        # Ollama API is usually at /api/generate
        url = f"{base_url.rstrip('/')}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **config
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=60.0)
                if response.status_code == 400:
                    detail = response.json().get("error", "")
                    if "embed" in model.lower() or "nomic" in model.lower():
                        raise ValueError(f"Model '{model}' appears to be an embedding model. Use a chat/generation model like 'llama3' for prompts.")
                    raise ValueError(f"Ollama 400 Bad Request: {detail}")
                response.raise_for_status()
                return response.json().get("response", "")
            except httpx.ConnectError:
                raise ValueError(f"Could not connect to Ollama at {base_url}")
