from openai import OpenAI

from vidsift.config.models import AIConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.providers.base import AIProvider


class LMStudioProvider(AIProvider):
    def __init__(self, config: AIConfig) -> None:
        super().__init__(config)
        self.client = OpenAI(
            base_url=config.ai.base_url,
            api_key="lm-studio"
        )

    def generate(self, request: AIRequest) -> AIResponse:
        resp = self.client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return AIResponse(
            content=resp.choices[0].message.content,
            provider=ProviderName.LMSTUDIO,
            model=request.model,
        )

    def get_provider_name(self) -> ProviderName:
        return ProviderName.LMSTUDIO
