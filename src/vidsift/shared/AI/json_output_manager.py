import json
import logging

from pydantic import ValidationError

from vidsift.config.models import AppConfig
from vidsift.models.ai_json_requirements import (AIJSONBaseRequirements,
                                                 AIJSONRuntimeRequirements)
from vidsift.models.ai_models import AIRequest
from vidsift.shared.AI.errors import (AIError, EmptyAIResponseError,
                                      InvalidAIResponseFormatError)
from vidsift.shared.AI.executor import AIExecutor
from vidsift.shared.AI.prompt_manager import PromptManager
from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)


class AIJsonOutputManager:
    def __init__(self, config: AppConfig, requirements: AIJSONBaseRequirements) -> None:
        self.config: AppConfig = config
        self.output_format_instance = requirements.output_format_instance
        self.system_prompt_filename: str = requirements.system_prompt_filename
        self.retry_system_filename: str = requirements.retry_system_filename

    def run_ai_pipeline(self, requirements: AIJSONRuntimeRequirements):
        """
        Method to run the AI pipeline to get a valid JSON output from the AI, with retries if the output is not valid.
        """
        validation_prompt: PromptManager = PromptManager(self.system_prompt_filename, config=self.config)
        retry_system_prompt: PromptManager = PromptManager(self.retry_system_filename, config=self.config)
        ai_executor: AIExecutor = AIExecutor(config=self.config.ai, api_key=None)
        use_full_validate: bool = True

        logger.debug(
            "AI JSON output generation started.",
            extra={
                "event": LogEvent.AI_JSON_OUTPUT_STARTED,
                "model": requirements.ai_model,
                "max_attempts": self.config.ai.max_allowed_json_output_runs,
            },
        )

        for i in range(self.config.ai.max_allowed_json_output_runs):
            logger.debug(
                f"Starting attempt {i+1} of {self.config.ai.max_allowed_json_output_runs}",
                extra={
                    "event": LogEvent.AI_JSON_OUTPUT_STARTED,
                    "model": requirements.ai_model,
                    "attempt": i + 1,
                    "max_attempts": self.config.ai.max_allowed_json_output_runs,
                    "use_full_validation": use_full_validate,
                },
            )

            # on the first attempt or if the ai response is empty (use_full_validate is true)
            if use_full_validate:
                # get the prompt
                prompt: str = validation_prompt.generate_prompt(
                    pattern=requirements.first_attempt_pattern,
                    replacement=requirements.first_attempt_replacement,
                    append=requirements.first_attempt_append,
                )

            # for the attempts that come after, when response and error message exist
            else:
                # get the prompt
                prompt: str = retry_system_prompt.generate_prompt(
                    system_prompt=retry_system_prompt.generate_prompt(
                        pattern="$ERROR_MESSAGE",
                        replacement=error_msg,
                    ),
                    pattern="$PREVIOUS_AI_OUTPUT",
                    replacement=response,
                )

            try:
                ai_request: AIRequest = AIRequest(
                    prompt=prompt,
                    model=requirements.ai_model,
                    max_tokens=1000,
                )
                response: str = str(ai_executor.generate(request=ai_request).content)
                validated_response = self.validate_ai_response(ai_response=response)


            except EmptyAIResponseError as e:
                error_msg: str = str(e)
                response: str = ""

                logger.warning(
                    "AI returned an empty response.",
                    extra={
                        "event": LogEvent.AI_JSON_OUTPUT_FAILED,
                        "model": requirements.ai_model,
                        "attempt": i + 1,
                        "max_attempts": self.config.ai.max_allowed_json_output_runs,
                        "failure_reason": "empty_response",
                    },
                )

                use_full_validate: bool = True
                continue

            except InvalidAIResponseFormatError as e:
                use_full_validate: bool = False
                error_msg: str = str(e)

                logger.warning(
                    "AI returned invalid JSON output.",
                    extra={
                        "event": LogEvent.AI_JSON_OUTPUT_FAILED,
                        "model": requirements.ai_model,
                        "attempt": i + 1,
                        "max_attempts": self.config.ai.max_allowed_json_output_runs,
                        "failure_reason": "invalid_json_output",
                    },
                )

                continue
            else:
                logger.debug(
                    "AI JSON output generation completed.",
                    extra={
                        "event": LogEvent.AI_JSON_OUTPUT_COMPLETED,
                        "model": requirements.ai_model,
                        "attempt": i + 1,
                    },
                )

                return validated_response

        logger.error(
            "AI JSON output generation failed after all attempts.",
            extra={
                "event": LogEvent.AI_JSON_OUTPUT_FAILED,
                "model": requirements.ai_model,
                "max_attempts": self.config.ai.max_allowed_json_output_runs,
            },
        )

        raise AIError("After 3 attempts, the AI output does not match the required JSON")

    def validate_ai_response(self, ai_response: str):
        """
        Method to validate the response of the AI.
        That includes:
        - checking wether the JSON is parsable
        - checking wether the values in the JSON have the correct type
        Raises:
        InvalidAIResponseFormatError if JSON is invalid or JSON output structure is broken
        """

        logger.debug(
            "AI response validation started.",
            extra={
                "event": LogEvent.AI_RESPONSE_VALIDATION_STARTED,
                "response": ai_response,
            },
        )

        try:
            parsed_json = json.loads(ai_response)
            validate_response = self.output_format_instance.model_validate(parsed_json)

            logger.debug(
                "AI response validation completed.",
                extra={
                    "event": LogEvent.AI_RESPONSE_VALIDATION_COMPLETED,
                    "response": ai_response,
                },
            )

            return validate_response

        except json.JSONDecodeError as e:
            logger.warning(
                "AI response validation failed due to invalid JSON syntax.",
                extra={
                    "event": LogEvent.AI_RESPONSE_VALIDATION_FAILED,
                    "response": ai_response,
                    "failure_reason": "json_decode_error",
                },
            )

            raise InvalidAIResponseFormatError(f"AI output invalid, invalid JSON syntax: {str(e)}")

        except ValidationError as e:
            logger.warning(
                "AI response validation failed due to invalid JSON structure.",
                extra={
                    "event": LogEvent.AI_RESPONSE_VALIDATION_FAILED,
                    "response": ai_response,
                    "failure_reason": "schema_validation_error",
                },
            )

            raise InvalidAIResponseFormatError(f"Wrong JSON output structure: {str(e)}")
