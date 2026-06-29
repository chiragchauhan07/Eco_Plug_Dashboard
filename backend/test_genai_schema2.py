import asyncio
from google import genai
from google.genai import types
import pydantic
import traceback

class X(pydantic.BaseModel):
    name: str

async def main():
    client = genai.Client(api_key="dummy")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=X,
            )
        )
    except Exception as e:
        traceback.print_exc()

asyncio.run(main())
