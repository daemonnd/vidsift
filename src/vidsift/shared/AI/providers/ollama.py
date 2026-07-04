import requests
from ollama import ChatResponse, Client, RequestError, ResponseError, list
from pydantic import config

from vidsift.config.models import AIConfig, AppConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.errors import (AIModelError, AIRequestError,
                                      InvalidAIConfigError)
from vidsift.shared.AI.providers.base import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self, config: AIConfig, api_key: str | None = None) -> None:
        super().__init__(config)

    def _validate_data(self) -> None:
        if requests.get(self.config.base_url).status_code != 200:
            raise AIRequestError(f"Invalid base url: {self.config.base_url}")
        models = list()
        default_model_found = False
        validation_model_found = False
        summary_model_found = False

        for model in models["models"]:
            if model == self.config.default_model:
                default_model_found = True
            if model == self.config.validation_model:
                validation_model_found = True
            if model == self.config.summary_model:
                summary_model_found = True
        if not default_model_found:
            raise AIModelError(f"The default model {self.config.default_model} does not exist")
        elif not validation_model_found:
            raise AIModelError(f"The validation model {self.config.validation_model} does not exist")
        elif not summary_model_found:
            raise AIModelError(f"The summarization model {self.config.summary_model} does not exist")

    def generate(self, request: AIRequest) -> AIResponse:
        try:
            response: ChatResponse = Client(self.config.base_url).chat(
                model=request.model,
                    messages=[{"role": "user", "content": request.prompt}],
                    options={
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens if request.max_tokens is not None else 100
                    }
                )
        except ResponseError as e:
            raise AIModelError(f"An error occurred while running the AI model: {e}") from e
        except RequestError as e:
            raise AIRequestError(f"An error occured while making a request to the AI: {e}") from e
        else:
            return AIResponse(
                content=response.message.content,
                provider=ProviderName.OLLAMA,
                model=request.model,
            )

    def get_provider_name(self) -> ProviderName:
        return ProviderName.OLLAMA

