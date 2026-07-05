from abc import ABC, abstractmethod

from vidsift.config.models import AIConfig, AppConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName


class AIProvider(ABC):
    """
    Provider Base class for AI.
    All AI providers should inherit from this class and implement the generate method.
    """
    def __init__(self, config: AIConfig) -> None:
        self.config: AIConfig = config

    @abstractmethod
    def _validate_data(self) -> None:
        """
        Method to validate the data before making a request to the AI.
        It checks the base url, api key, and other required parameters.
        Raises:
        - AIRequestError if the base url is unhealthy
        - AIModelError for model-related errors
        """
        pass


    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        """
        Method to run the AI
        Raises:
        - EmptyAIResponseError if the AI response is empty
        - AIModelError if an error with the model occured
        - AIRequestError if an error occured while making a request to the AI
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> ProviderName:
        pass
