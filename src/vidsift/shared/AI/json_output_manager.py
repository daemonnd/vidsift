import json

from pydantic import ValidationError

from vidsift.config.parser import MAX_ALLOWED_AI_JSON_OUTPUT_RUNS, ConfigParser
from vidsift.models.ai_json_requirements import (AIJSONBaseRequirements,
                                                 AIJSONRuntimeRequirements)
from vidsift.shared.AI.errors import (AIError, EmptyAIResponseError,
                                      InvalidAIResponseFormatError)
from vidsift.shared.AI.run_model import AIUsageManager
from vidsift.shared.errorprotocol import logger

log: logger = logger()
config_parser: ConfigParser = ConfigParser()


class AIJsonOutputManager:
    def __init__(self, requirements: AIJSONBaseRequirements) -> None:
        self.output_format_instance = requirements.output_format_instance
        self.system_prompt_filename: str = requirements.system_prompt_filename
        self.retry_system_filename: str = requirements.retry_system_filename
    def run_ai_pipeline(self, requirements: AIJSONRuntimeRequirements):
        """
        Method to run the metadata validation that should output raw json, manages the execution of that with retries
        """
        validation_ai: AIUsageManager = AIUsageManager(self.system_prompt_filename)
        retry_system_ai: AIUsageManager = AIUsageManager(self.retry_system_filename)
        ai_executor: AIUsageManager = AIUsageManager("")
        for i in range(MAX_ALLOWED_AI_JSON_OUTPUT_RUNS):
            log.log_info(f"Starting attempt {i+1} of {MAX_ALLOWED_AI_JSON_OUTPUT_RUNS}")

            # on the first attempt
            if i == 0:
                # get the prompt
                prompt: str = validation_ai.generate_prompt(
                    pattern=requirements.first_attempt_pattern, 
                    replacement=requirements.first_attempt_replacement,
                    append=requirements.first_attempt_append,
                )
                print(f"prompt: {prompt}")

            # for the attempts that come after, when response and error message exist
            else:
                # get the prompt
                prompt: str = retry_system_ai.generate_prompt(
                            system_prompt=retry_system_ai.generate_prompt(
                            pattern="$ERROR_MESSAGE",
                            replacement=error_msg,
                        ),
                        pattern="$PREVIOUS_AI_OUTPUT",
                        replacement=response,
                    )
                print(f"prompt: {prompt}")
            try:
                response: str = ai_executor.run_ai(prompt=prompt, model=requirements.ai_model)
                print(f"response: {response}")
                return self.validate_ai_response(ai_response=response)
            except EmptyAIResponseError as e:
                error_msg: str = str(e)
                response: str = ""
                log.log_warning(f"EmptyAIResponseError: {str(e)}")
            except InvalidAIResponseFormatError as e:
                error_msg: str = str(e)
                log.log_warning(f"The AI did output invalid JSON: {str(e)}")
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
            print(f"parsed json: {parsed_json}")
            validate_response = self.output_format_instance.model_validate(parsed_json)
            print("model json schema")
            print(self.output_format_instance.model_json_schema())
            return validate_response
        except json.JSONDecodeError as e:
            raise InvalidAIResponseFormatError(f"AI output invalid, invalid JSON syntax: {str(e)}")
        except ValidationError as e:
            raise InvalidAIResponseFormatError(f"Wrong JSON output structure: {str(e)}")



