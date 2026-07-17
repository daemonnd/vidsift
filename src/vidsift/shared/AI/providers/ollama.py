import requests
from ollama import ChatResponse, Client, RequestError, ResponseError
from ollama import list as ollama_list
from requests.exceptions import ConnectionError

from vidsift.config.models import AIConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName
from vidsift.shared.AI.errors import AIModelError, AIRequestError
from vidsift.shared.AI.providers.base import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self, config: AIConfig) -> None:
        super().__init__(config)
        self._validate_data()

    def _validate_data(self) -> None:
        if not self.config.skip_ai_checks:
            try:
                if requests.get(self.config.base_url).status_code != 200:
                    raise AIRequestError(f"Invalid base url: {self.config.base_url}")
            except ConnectionError as e:
                raise AIRequestError(f"Failed to connect to base url '{self.config.base_url}': {str(e)}") from e

        response = ollama_list()
        models = response["models"] if isinstance(response, dict) else response.models

        metadata_validation_model = any(m.model == self.config.tasks.metadata_validation.reference for m in models)
        transcript_validation_model = any(m.model == self.config.tasks.transcript_validation.reference for m in models)
        chunk_summary_model = any(m.model == self.config.tasks.chunk_summary.reference for m in models)
        overall_summary_model = any(m.model == self.config.tasks.overall_summary.reference for m in models)

        if not metadata_validation_model:
            raise AIModelError(f"The metadata validation model {self.config.tasks.metadata_validation.reference} does not exist")
        if not transcript_validation_model:
            raise AIModelError(f"The transcript validation model {self.config.tasks.transcript_validation.reference} does not exist")
        if not chunk_summary_model:
            raise AIModelError(f"The chunk summary model {self.config.tasks.chunk_summary.reference} does not exist")
        if not overall_summary_model:
            raise AIModelError(f"The overall summary model {self.config.tasks.chunk_summary.reference} does not exist")


    def generate(self, request: AIRequest) -> AIResponse:
        try:
            response: ChatResponse = Client(self.config.base_url).chat(
                model=request.model,
                    messages=[{"role": "user", "content": request.prompt}],
                    options={
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens,
                        "num_ctx": request.context_length
                    },
                think=request.thinking
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

