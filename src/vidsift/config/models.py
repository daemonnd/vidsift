from pydantic import BaseModel, ConfigDict, Field


class AIConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    default_model: str
    validation_model: str
    summary_model: str
    max_allowed_json_output_runs: int = Field(ge=0,le=5)


class PreValidationThresholdConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    title_punctuation_ratio: float = Field(ge=0.0, le=1)
    title_uppercase_ratio: float = Field(ge=0.0, le=1)
    title_emoji_ratio: float = Field(ge=0.0, le=1)
    title_clickbait_ratio: float = Field(ge=0.0, le=1)
    transcript_clickbait_ratio: float = Field(ge=0.0, le=1)

class PreValidationWeightsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    title_punctuation_weight: float = Field(ge=0.0, le=10)
    title_uppercase_weight: float = Field(ge=0.0, le=10)
    title_emoji_weight: float = Field(ge=0.0, le=10)
    title_clickbait_weight: float = Field(ge=0.0, le=10)
    transcript_clickbait_weight: float = Field(ge=0.0, le=10)

class PreValidationConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_allowed: PreValidationThresholdConfig
    weak: PreValidationThresholdConfig
    weights: PreValidationWeightsConfig

class ValidationConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled: bool
    transcript_chunk_char_size: int = Field(ge=100)
    pre_validation: PreValidationConfig

class SummarizationConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled: bool
    char_chunk_size: int = Field(ge=100)

class DownloadsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled: bool
    output_dir: str

class ChannelConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    name: str


class AppConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    ai: AIConfig
    validation: ValidationConfig
    summarization: SummarizationConfig
    downloads: DownloadsConfig
    channels: list[ChannelConfig]

