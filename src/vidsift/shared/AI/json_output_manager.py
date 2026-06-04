import json

from pydantic import ValidationError

from vidsift.config import CONFIG
from vidsift.models.ai_json_requirements import (AIJSONBaseRequirements,
                                                 AIJSONRuntimeRequirements)
from vidsift.shared.AI.errors import (AIError, EmptyAIResponseError,
                                      InvalidAIResponseFormatError)
from vidsift.shared.AI.run_model import AIUsageManager
from vidsift.shared.errorprotocol import logger

log: logger = logger()


class AIJsonOutputManager:
    def __init__(self, requirements: AIJSONBaseRequirements) -> None:
        self.output_format_instance = requirements.output_format_instance
        self.system_prompt_filename: str = requirements.system_prompt_filename
        self.retry_system_filename: str = requirements.retry_system_filename
    def run_ai_pipeline(self, requirements: AIJSONRuntimeRequirements):
        """
        Method to run the AI pipeline to get a valid JSON output from the AI, with retries if the output is not valid.
        """
        validation_ai: AIUsageManager = AIUsageManager(self.system_prompt_filename)
        retry_system_ai: AIUsageManager = AIUsageManager(self.retry_system_filename)
        ai_executor: AIUsageManager = AIUsageManager("")
        use_full_validate: bool = True
        for i in range(CONFIG.ai.max_allowed_json_output_runs):
            log.log_info(f"Starting attempt {i+1} of {CONFIG.ai.max_allowed_json_output_runs}")

            # on the first attempt or if the ai response is empty (use_full_validate is true)
            if use_full_validate:
                log.log_info("Using full validation for this attempt")
                # get the prompt
                prompt: str = validation_ai.generate_prompt(
                    pattern=requirements.first_attempt_pattern, 
                    replacement=requirements.first_attempt_replacement,
                    append=requirements.first_attempt_append,
                )

            # for the attempts that come after, when response and error message exist
            else:
                log.log_info("Using retry validation for this attempt")
                # get the prompt
                prompt: str = retry_system_ai.generate_prompt(
                            system_prompt=retry_system_ai.generate_prompt(
                            pattern="$ERROR_MESSAGE",
                            replacement=error_msg,
                        ),
                        pattern="$PREVIOUS_AI_OUTPUT",
                        replacement=response,
                    )
            try:
                response: str = ai_executor.run_ai(prompt=prompt, model=requirements.ai_model)
                log.log_debug(f"response: {response}")
                return self.validate_ai_response(ai_response=response)
            except EmptyAIResponseError as e:
                error_msg: str = str(e)
                response: str = ""
                log.log_warning(f"EmptyAIResponseError: {str(e)}")
                use_full_validate: bool = True
                continue
            except InvalidAIResponseFormatError as e:
                use_full_validate: bool = False
                error_msg: str = str(e)
                log.log_warning(f"The AI did output invalid JSON: {str(e)}")
                continue
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

        try:
            parsed_json = json.loads(ai_response)
            log.log_debug(f"parsed json: {parsed_json}")
            validate_response = self.output_format_instance.model_validate(parsed_json)
            log.log_debug(f"Model JSON Schema: \n{self.output_format_instance.model_json_schema()}")
            return validate_response
        except json.JSONDecodeError as e:
            raise InvalidAIResponseFormatError(f"AI output invalid, invalid JSON syntax: {str(e)}")
        except ValidationError as e:
            raise InvalidAIResponseFormatError(f"Wrong JSON output structure: {str(e)}")

