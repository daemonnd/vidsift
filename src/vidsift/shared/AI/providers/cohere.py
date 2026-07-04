from vidsift.config.models import AppConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.providers.base import AIProvider


class CohereProvider(AIProvider):
    def __init__(self, config: AppConfig) -> None:
        super().__init__(config)
        self.config: AppConfig = config

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content="",
            provider=ProviderName.COHERE,
            model=request.model,
            success=True,
        )

    def get_provider_name(self) -> ProviderName:
        return ProviderName.COHERE
