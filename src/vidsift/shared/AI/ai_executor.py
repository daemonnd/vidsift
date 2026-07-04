"""
File to manage AI excecution
"""
from vidsift.config.models import AppConfig
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
    def __init__(self, config: AppConfig) -> None:
        self.config: AppConfig = config

