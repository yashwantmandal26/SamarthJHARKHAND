import os
import json
import asyncio
import httpx
from backend.config import settings
from backend.llm.prompts import Prompts


class OllamaClient:
    """Local LLM client using Ollama REST API."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.system_instruction = Prompts.SYSTEM_INSTRUCTION
        print(f"[LLM] Using Ollama ({self.model}) at {self.base_url}")

    async def generate_response(self, prompt: str, history: list = None, response_schema=None) -> str:
        """Generate a response using Ollama's local API."""

        messages = [{"role": "system", "content": self.system_instruction}]

        # Add history
        if history:
            for msg in history:
                role = "assistant" if msg["role"] == "assistant" else "user"
                messages.append({"role": role, "content": msg["content"]})

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        # Build request body
        body = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        # If structured JSON is requested, enable JSON mode
        if response_schema:
            body["format"] = "json"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]

    async def generate_response_stream(self, prompt: str, history: list = None, response_schema=None):
        """Generate response sequentially (stream) using Ollama's local API."""
        messages = [{"role": "system", "content": self.system_instruction}]
        
        # Add history
        if history:
            for msg in history:
                role = "assistant" if msg["role"] == "assistant" else "user"
                messages.append({"role": role, "content": msg["content"]})
                
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": self.model,
            "messages": messages,
            "stream": True,  # streaming enabled
        }
        
        if response_schema:
            body["format"] = "json"

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=body) as response:
                response.raise_for_status()
                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            data = json.loads(chunk)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue


class GeminiClient:
    """Cloud LLM client using Google Gemini API."""

    def __init__(self):
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.genai = genai
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=Prompts.SYSTEM_INSTRUCTION,
        )
        print(f"[LLM] Using Gemini ({settings.GEMINI_MODEL})")

    async def generate_response(self, prompt: str, history: list = None, response_schema=None, max_retries: int = 3) -> str:
        """Generate response with retry logic for rate limits."""

        formatted_history = []
        if history:
            for msg in history:
                role = "model" if msg["role"] == "assistant" else "user"
                formatted_history.append({"role": role, "parts": [msg["content"]]})

        chat = self.model.start_chat(history=formatted_history)

        generation_config = self.genai.GenerationConfig()
        if response_schema:
            generation_config.response_mime_type = "application/json"
            generation_config.response_schema = response_schema

        last_error = None
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    chat.send_message,
                    prompt,
                    generation_config=generation_config,
                )
                return response.text
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                if "429" in str(e) or "quota" in error_str or "rate" in error_str:
                    wait_time = (2 ** attempt) + 1
                    print(f"[Gemini] Rate limited (attempt {attempt+1}/{max_retries}). Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise e

        raise last_error

    async def generate_response_stream(self, prompt: str, history: list = None, response_schema=None, max_retries: int = 3):
        """Generate response sequentially (stream) using Gemini API."""
        formatted_history = []
        if history:
            for msg in history:
                role = "model" if msg["role"] == "assistant" else "user"
                formatted_history.append({"role": role, "parts": [msg["content"]]})

        chat = self.model.start_chat(history=formatted_history)

        generation_config = self.genai.GenerationConfig()
        if response_schema:
            generation_config.response_mime_type = "application/json"
            generation_config.response_schema = response_schema

        last_error = None
        for attempt in range(max_retries):
            try:
                if hasattr(chat, "send_message_async"):
                    response = await chat.send_message_async(
                        prompt,
                        generation_config=generation_config,
                        stream=True
                    )
                    async for chunk in response:
                        if chunk.text:
                            yield chunk.text
                    return
                else: 
                    response = await asyncio.to_thread(
                        chat.send_message,
                        prompt,
                        generation_config=generation_config,
                        stream=True
                    )
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                    return
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                if "429" in str(e) or "quota" in error_str or "rate" in error_str:
                    wait_time = (2 ** attempt) + 1
                    print(f"[Gemini] Rate limited (attempt {attempt+1}/{max_retries}). Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise e
        raise last_error


def create_llm_client():
    """Factory: create the right client based on LLM_PROVIDER env."""
    provider = settings.LLM_PROVIDER.lower()
    if provider == "ollama":
        return OllamaClient()
    elif provider == "gemini":
        return GeminiClient()
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'. Use 'ollama' or 'gemini'.")


llm_client = create_llm_client()
