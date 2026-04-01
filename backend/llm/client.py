import os
import google.generativeai as genai
from backend.config import settings

# Initialize Gemini Client
genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiClient:
    def __init__(self):
        # We use Flash for speed.
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction="You are Samarth, a knowledgeable, polite, and helpful Government Officer AI assistant for the citizens of Jharkhand, India."
        )

    async def generate_response(self, prompt: str, history: list = None, response_schema=None) -> str:
        """
        Generates a standard text or structured response.
        history expects a list of dicts: [{'role': 'user', 'content': '...'}]
        """
        
        # Convert our history format to Gemini's format
        formatted_history = []
        if history:
             for msg in history:
                 role = "model" if msg['role'] == "assistant" else "user"
                 formatted_history.append({"role": role, "parts": [msg['content']]})
                 
        chat = self.model.start_chat(history=formatted_history)
        
        # If schema is provided, we can ask for JSON output
        # For gemini-2.0, we can pass expected response schema
        generation_config = genai.GenerationConfig()
        if response_schema:
             generation_config.response_mime_type = "application/json"
             # Gemini API accepts response_schema in generation_config
             generation_config.response_schema = response_schema
             
        response = chat.send_message(
            prompt,
            generation_config=generation_config
        )
        return response.text

llm_client = GeminiClient()
