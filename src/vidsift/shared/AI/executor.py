"""
File to manage AI excecution
"""
import logging

from vidsift.config.models import AIConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.errors import AIError, EmptyAIResponseError
#from vidsift.shared.AI.providers.anthropic import AnthropicProvider
from vidsift.shared.AI.providers.base import AIProvider
#from vidsift.shared.AI.providers.cohere import CohereProvider
#from vidsift.shared.AI.providers.custom import CustomProvider
#from vidsift.shared.AI.providers.google import GoogleProvider
from vidsift.shared.AI.providers.lmstudio import LMStudioProvider
#from vidsift.shared.AI.providers.microsoft import MicrosoftProvider
#from vidsift.shared.AI.providers.mistral import MistralProvider
from vidsift.shared.AI.providers.ollama import OllamaProvider
from vidsift.shared.logging.log_event_fields import LogEvent

#from vidsift.shared.AI.providers.openai import OpenAIProvider
#from vidsift.shared.AI.providers.xai import XAIProvider

logger = logging.getLogger(__name__)

class AIExecutor:
    def __init__(self, config: AIConfig) -> None:
        self.config: AIConfig = config
        match self.config.provider:
            case "ollama":
                self.ai: AIProvider = OllamaProvider(config=config)
            case "lmstudio":
                self.ai: AIProvider = LMStudioProvider(config=config)

    def generate(self, request: AIRequest) -> AIResponse:
        logger.debug(
            "Starting new AI Request",
            extra={
                "event": LogEvent.AI_RESPONSE_GENERATION_STARTED,
                "model": request.model,
                "temperature": request.temperature,
                "context_length": request.context_length,
                "thinking": request.thinking,
                "max_tokens": request.max_tokens,
                "prompt": request.prompt
            }
        )
        try:
            response: AIResponse = self.ai.generate(request=request)
        except AIError:
            logger.debug(
                "AI response generation failed",
                extra={
                    "event": LogEvent.AI_RESPONSE_GENERATION_FAILED,
                    "model": request.model,
                    "temperature": request.temperature,
                    "context_length": request.context_length,
                    "thinking": request.thinking,
                    "max_tokens": request.max_tokens,
                    "prompt": request.prompt
                }
            )
            raise
        except Exception as e:
            logger.debug(
                "AI response generation failed",
                extra={
                    "event": LogEvent.AI_RESPONSE_GENERATION_FAILED,
                    "model": request.model,
                    "temperature": request.temperature,
                    "context_length": request.context_length,
                    "thinking": request.thinking,
                    "max_tokens": request.max_tokens,
                    "prompt": request.prompt
                }
            )
            raise AIError(f"{type(e).__name__}: {str(e)}")
        else:
            logger.debug(
                "AI response generation succeeded (no errors)",
                extra={
                    "event": LogEvent.AI_RESPONSE_GENERATION_COMPLETED,
                    "model": request.model,
                    "temperature": request.temperature,
                    "context_length": request.context_length,
                    "thinking": request.thinking,
                    "max_tokens": request.max_tokens,
                    "prompt": request.prompt
                }
            )
            if not response.content or not response.content.replace(" ", ""):
                raise EmptyAIResponseError("The response of the AI is empty")
            else:
                return response # response.content has to be a str because of the previous checks
    def get_provider_name(self) -> ProviderName:
        return self.ai.get_provider_name()

