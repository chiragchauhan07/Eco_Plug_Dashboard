from abc import ABC, abstractmethod
from typing import Any, List, Type
from pydantic import BaseModel

from app.schemas.ai import ChatMessage, ChatResponse

class BaseProvider(ABC):
    """
    Abstract base class for AI Providers (Gemini, OpenAI, Claude, etc.)
    """

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate a simple text response from a prompt.
        """
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Type[BaseModel], **kwargs: Any) -> BaseModel:
        """
        Generate a structured response adhering to a given Pydantic schema.
        """
        pass

    @abstractmethod
    async def chat(self, messages: List[ChatMessage], **kwargs: Any) -> ChatResponse:
        """
        Handle a multi-turn conversation.
        """
        pass
