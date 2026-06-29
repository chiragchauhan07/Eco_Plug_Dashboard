from typing import Any, List, Type
from pydantic import BaseModel

from google import genai
from google.genai import types

from app.schemas.ai import ChatMessage, ChatResponse
from app.ai.providers.base import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else genai.Client()

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate a simple text response.
        """
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return str(response.text) if response.text else ""

    def _clean_json_response(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    async def generate_structured(self, prompt: str, schema: Type[BaseModel], **kwargs: Any) -> BaseModel:
        """
        Generate a structured response adhering to the Pydantic schema.
        """
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=kwargs.get("temperature", 0.2),
            ),
        )
        
        # Parse the JSON string response into the Pydantic model
        cleaned_text = self._clean_json_response(response.text or "{}")
        return schema.model_validate_json(cleaned_text)

    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        """
        Handle a multi-turn conversation.
        Google GenAI SDK expects contents list.
        """
        contents = []
        for msg in messages:
            role = "user" if msg.role == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents
        )
        return ChatResponse(reply=str(response.text) if response.text else "")
