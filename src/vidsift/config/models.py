import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConsoleLoggingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled: bool
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    dependency_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class FileLoggingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled: bool
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    dependency_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    rotation: Literal["S", "M", "H", "D", "midnight"]
    retain_days: int = Field(ge=0, le=1000)
    utc_time: bool

class LoggingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    console: ConsoleLoggingConfig
    file: FileLoggingConfig

class VideoFetchingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    rss_bozo_level: Literal["permissive", "strict", "ignore", "debug"]

class AIConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    host: str
    provider: Literal["ollama", "openai", "anthropic", "lmstudio", "google_gemini", "xai"]
    default_model: str
    validation_model: str
    summary_model: str
    max_allowed_json_output_runs: int = Field(ge=0,le=5)

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        if v.startswith("http://") or v.startswith("https://"):
            pass
        else:
            raise ValueError("host must start with http:// or https://")

        return v


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
    output_dir: str

class DownloadsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    enabled: bool
    output_dir: str

class ChannelConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    name: str
    action: Literal["validate", "download", "summarize"]

    @field_validator("id")
    @classmethod
    def validate_channel_id(cls, v: str) -> str:
        if len(v) != 24:
            raise ValueError(f"channel_id must be 24 chars, got {len(v)}")

        if not v.startswith("UC"):
            raise ValueError("channel_id must start with 'UC'")

        return v
class YtDlpConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_retries: int | Literal["infinite"] = Field(ge=0)
    sleep_requests: int = Field(ge=0)
    cookies_from_browser: str
    quiet: bool
    merge_output_format: str
    format: str
    additional_args: str

    @field_validator("additional_args")
    @classmethod
    def validate_additional_args(cls, v: str) -> str:
        try:
            return json.dumps(v)
        except Exception as e:
            raise ValueError(f"additional_args are not a JSON-formatted string: {str(e)}")

class VideoProcessingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_retry_attempts: int = Field(le=10, ge=-1)
    days_uploaded_before: int = Field(ge=0)
    min_vid_delay: int = Field(ge=30)
    random_vid_delay: int = Field(ge=10)
    yt_dlp: YtDlpConfig


class AppConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    logging: LoggingConfig
    video_fetching: VideoFetchingConfig
    ai: AIConfig
    video_processing: VideoProcessingConfig
    validation: ValidationConfig
    summarization: SummarizationConfig
    downloads: DownloadsConfig
    channels: list[ChannelConfig]

