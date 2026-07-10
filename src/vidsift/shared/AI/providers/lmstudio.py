import lmstudio as lms

from vidsift.config.models import AIConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.errors import AIModelError, AIRequestError
from vidsift.shared.AI.providers.base import AIProvider


class LMStudioProvider(AIProvider):
    def __init__(self, config: AIConfig) -> None:
        self.client = lms.Client(api_host=config.base_url)

        super().__init__(config)

        self._validate_data()

    def _validate_data(self) -> None:
        try:
            models = self.client.list_downloaded_models()
        except Exception as e:
            raise AIRequestError(
                f"LM Studio base_url unreachable: {self.config.base_url}"
            ) from e

        model_ids = {model.model_key for model in models}

        if self.config.tasks.metadata_validation.reference not in model_ids:
            raise AIModelError(
                f"Metadata validation model missing: {self.config.tasks.metadata_validation.reference}"
            )
        if self.config.tasks.transcript_validation.reference not in model_ids:
            raise AIModelError(
                f"Transcript validation model missing: {self.config.tasks.transcript_validation.reference}"
            )
        if self.config.tasks.chunk_summary.reference not in model_ids:
            raise AIModelError(
                f"Chunk summary model missing: {self.config.tasks.chunk_summary.reference}"
            )
        if self.config.tasks.overall_summary.reference not in model_ids:
            raise AIModelError(
                f"Overall summary model missing: {self.config.tasks.overall_summary.reference}"
            )

    def generate(self, request: AIRequest) -> AIResponse:
        try:
            model = self.client.llm.model(
                request.model,
                config={
                    "contextLength": request.context_length,
                },
            )
            response = model.respond(
                request.prompt,
                config={
                    "temperature": request.temperature,
                    "maxTokens": request.max_tokens,
                },
            )

        except Exception as e:
            raise AIRequestError(
                f"LM Studio request failed: {type(e).__name__}: {e}"
            ) from e

        content = getattr(response, "content", None)

        return AIResponse(
            content=content,
            provider=ProviderName.LMSTUDIO,
            model=request.model,
        )

    def get_provider_name(self) -> ProviderName:
        return ProviderName.LMSTUDIO
