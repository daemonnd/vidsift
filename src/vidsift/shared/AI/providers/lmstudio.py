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

        if self.config.default_model not in model_ids:
            raise AIModelError(
                f"Default model missing: {self.config.default_model}"
            )

        if self.config.validation_model not in model_ids:
            raise AIModelError(
                f"Validation model missing: {self.config.validation_model}"
            )

        if self.config.summary_model not in model_ids:
            raise AIModelError(
                f"Summary model missing: {self.config.summary_model}"
            )

    def generate(self, request: AIRequest) -> AIResponse:
        try:
            model = self.client.llm.model(request.model)

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
