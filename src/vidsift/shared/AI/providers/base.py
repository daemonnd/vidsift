from abc import ABC, abstractmethod

from vidsift.config.models import AppConfig
from vidsift.models.ai_models import AIRequest, AIResponse, ProviderName


class AIProvider(ABC):
    """
    Provider Base class for AI.
    All AI providers should inherit from this class and implement the generate method.
    """
    def __init__(self, config: AppConfig) -> None:
        self.config: AppConfig = config

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
