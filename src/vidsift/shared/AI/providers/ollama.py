import requests
from ollama import ChatResponse, Client, RequestError, ResponseError
from ollama import list as ollama_list

from vidsift.config.models import AIConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.errors import AIModelError, AIRequestError
from vidsift.shared.AI.providers.base import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self, config: AIConfig, api_key: str | None = None) -> None:
        super().__init__(config)

    def _validate_data(self) -> None:
        if requests.get(self.config.base_url).status_code != 200:
            raise AIRequestError(f"Invalid base url: {self.config.base_url}")

        response = ollama_list()
        models = response["models"] if isinstance(response, dict) else response.models

        default_model_found = any(m.model == self.config.default_model for m in models)
        validation_model_found = any(m.model == self.config.validation_model for m in models)
        summary_model_found = any(m.model == self.config.summary_model for m in models)

        if not default_model_found:
            raise AIModelError(f"The default model {self.config.default_model} does not exist")
        if not validation_model_found:
            raise AIModelError(f"The validation model {self.config.validation_model} does not exist")
        if not summary_model_found:
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

