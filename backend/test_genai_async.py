import asyncio
from google import genai
import traceback

async def main():
    client = genai.Client(api_key="dummy")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello"
        )
    except Exception as e:
        traceback.print_exc()

asyncio.run(main())
