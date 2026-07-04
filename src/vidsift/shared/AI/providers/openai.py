from openai import OpenAI

from vidsift.config.models import AppConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.providers.base import AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, config: AppConfig) -> None:
        super().__init__(config)
        self.client = OpenAI(api_key=config.openai_api_key)  # or your key source

    def generate(self, request: AIRequest) -> AIResponse:
        resp = self.client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return AIResponse(
            content=resp.choices[0].message.content,
            provider=ProviderName.OPENAI,
            model=request.model,
        )

    def get_provider_name(self) -> ProviderName:
        return ProviderName.OPENAI
