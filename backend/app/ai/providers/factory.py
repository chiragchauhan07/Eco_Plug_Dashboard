import logging

from app.core.config import settings
from app.ai.providers.base import BaseProvider
from app.ai.providers.gemini import GeminiProvider

logger = logging.getLogger(__name__)

class ProviderFactory:
    """
    Factory for instantiating AI providers based on configuration.
    """

    @staticmethod
    def get_provider() -> BaseProvider:
        provider_name = getattr(settings, "AI_PROVIDER", "gemini").lower()
        
        if provider_name == "gemini":
            if not getattr(settings, "GEMINI_API_KEY", None):
                logger.warning("GEMINI_API_KEY is not set in configuration. Relying on default credentials (e.g. Vertex AI).")
            return GeminiProvider(api_key=getattr(settings, "GEMINI_API_KEY", None))
            
        elif provider_name == "openai":
            # Ready for future implementation
            raise NotImplementedError("OpenAI provider is not yet implemented.")
            
        elif provider_name == "claude":
            # Ready for future implementation
            raise NotImplementedError("Claude provider is not yet implemented.")
            
        elif provider_name == "ollama":
            # Ready for future implementation
            raise NotImplementedError("Ollama provider is not yet implemented.")
            
        else:
            raise ValueError(f"Unknown AI provider specified: {provider_name}")
