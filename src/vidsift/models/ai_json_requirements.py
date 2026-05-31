from dataclasses import dataclass

from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.validation.validation_result import ValidationResult


@dataclass
class AIJSONBaseRequirements:
    system_prompt_filename: str
    retry_system_filename: str
    output_format_instance: MetadataValidationResult | ValidationResult
    

@dataclass
class AIJSONRuntimeRequirements:
    ai_model: str

    first_attempt_pattern: str
    first_attempt_replacement: str = ""
    first_attempt_prepend: str = ""
    first_attempt_append: str = ""

    #retry_attempts_pattern: str # not needed because it will be $ERROR_MESSAGE and $PREVIOUS_AI_OUTPUT
    #retry_attempts_replacement: str = "" # not needed because it will be the error message
    retry_attempts_prepend: str = ""
    retry_attempts_append: str = ""

