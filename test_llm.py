import asyncio
from backend.llm.client import llm_client
from backend.llm.prompts import Prompts
from backend.core.orchestrator import IntentExtractionSchema

async def main():
    message = "i am 25 and female"
    extraction_prompt = f"Previous chat context: []\n\nUser Message: {message}\n\nExtract the intent, profile updates, and query parameters."
    
    print("Calling LLM...")
    try:
        raw_extraction = await llm_client.generate_response(
            prompt=extraction_prompt, 
            history=[{"role": "user", "content": Prompts.INTENT_EXTRACTION_SYSTEM}],
            response_schema=IntentExtractionSchema
        )
        print("Raw output:")
        print(repr(raw_extraction))
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    asyncio.run(main())
