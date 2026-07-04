"""
File to manage AI excecution
"""
from vidsift.config.models import AIConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.errors import AIError, EmptyAIResponseError
from vidsift.shared.AI.providers.anthropic import AnthropicProvider
from vidsift.shared.AI.providers.base import AIProvider
from vidsift.shared.AI.providers.cohere import CohereProvider
from vidsift.shared.AI.providers.custom import CustomProvider
from vidsift.shared.AI.providers.google import GoogleProvider
from vidsift.shared.AI.providers.lmstudio import LMStudioProvider
from vidsift.shared.AI.providers.microsoft import MicrosoftProvider
from vidsift.shared.AI.providers.mistral import MistralProvider
from vidsift.shared.AI.providers.ollama import OllamaProvider
from vidsift.shared.AI.providers.openai import OpenAIProvider
from vidsift.shared.AI.providers.xai import XAIProvider


class AIEcecutor:
    def __init__(self, config: AIConfig) -> None:
        self.config: AIConfig = config
        match self.config.provider:
            case "ollama":
                self.ai: AIProvider = OllamaProvider(config=config)
    def generate(self, request: AIRequest) -> AIResponse:
        try:
            response: AIResponse = self.ai.generate(request=request)
        except AIError:
            raise
        except Exception as e:
            raise AIError(f"{type(e)}: {str(e)}")
        else:
            if not response.content or not response.content.replace(" ", ""):
                raise EmptyAIResponseError("The response of the AI is empty")
            else:
                return response
    def get_provider_name(self) -> ProviderName:
        return self.ai.get_provider_name()

