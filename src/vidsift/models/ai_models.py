from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProviderName(str, Enum):
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    CUSTOM = "custom"
    GOOGLE = "google"
    LMSTUDIO = "lmstudio"
    MICROSOFT = "microsoft"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    OPENAI = "openai"
    XAI = "xai"


@dataclass
class AIRequest:
    prompt: str
    model: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class AIResponse:
    content: str
    provider: ProviderName
    model: str
    success: bool = True
