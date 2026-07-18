from dataclasses import dataclass
from enum import Enum


class ProviderName(str, Enum):
    #ANTHROPIC = "anthropic"
    #COHERE = "cohere"
    #CUSTOM = "custom"
    #GOOGLE = "google"
    LMSTUDIO = "lmstudio"
    #MICROSOFT = "microsoft"
    #MISTRAL = "mistral"
    OLLAMA = "ollama"
    #OPENAI = "openai"
    #XAI = "xai"


@dataclass
class AIRequest:
    prompt: str
    model: str
    max_tokens: int
    context_length: int
    thinking: bool
    temperature: float = 0.7


@dataclass
class AIResponse:
    content: str
    provider: ProviderName
    model: str
