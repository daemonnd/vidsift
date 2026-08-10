from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
    yt_dlp_video_amount: int = Field(ge=0)


class SpecificAITaskConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    reference: str
    context_length: int = Field(ge=1024)
    max_tokens: int = Field(ge=50)
    thinking: bool

    @model_validator(mode="after")
    def validate_context(self):
        if self.max_tokens > self.context_length:
            raise ValueError(
                f"max_tokens value of {self.max_tokens} cannot exeed context_length which is {self.context_length}"
            )

        return self


class AITasksConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    # validation
    metadata_validation: SpecificAITaskConfig
    transcript_validation: SpecificAITaskConfig

    # summary
    chunk_summary: SpecificAITaskConfig
    overall_summary: SpecificAITaskConfig


class AIConfig(BaseModel):
    # context can't be more than max tokens
    model_config = ConfigDict(frozen=True)

    base_url: str
    provider: Literal["ollama", "lmstudio"]
    tasks: AITasksConfig

    max_allowed_json_output_runs: int = Field(ge=0, le=5)
    skip_ai_checks: bool = False


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
    # enabled: bool
    transcript_chunk_char_size: int = Field(ge=100)
    pre_validation: PreValidationConfig


class SummarizationConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    # enabled: bool
    char_chunk_size: int = Field(ge=100)
    output_dir: str


class DownloadsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    # enabled: bool
    output_dir: str


class ChannelConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    action: Literal["validate", "download", "summarize"]
    instruction: str | None = None

    @field_validator("id")
    @classmethod
    def validate_channel_id(cls, v: str) -> str:
        if len(v) != 24:
            raise ValueError(f"channel_id must be 24 chars, got {len(v)}")

        if not v.startswith("UC"):
            raise ValueError("channel_id must start with 'UC'")

        return v

    @model_validator(mode="after")
    def validate_instruction(self) -> "ChannelConfig":
        if self.action != "validate":
            return self

        if self.instruction is None:
            raise ValueError("instruction is required when action is 'validate'")
        return self


class JSRuntimesConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: Literal["deno", "node", "bun", "quickjs"]
    path: str | None = None


class YtDlpBaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_retries: int | Literal["infinite"] = Field(ge=0)
    sleep_requests: int = Field(ge=0)
    cookies_from_browser: str
    quiet: bool
    js_runtimes: list[JSRuntimesConfig]


class YtDlpDownloadConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    merge_output_format: str
    format: str


class YtDlpConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    base: YtDlpBaseConfig
    download: YtDlpDownloadConfig


class VideoProcessingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    skip_interrupted_vids: bool
    skip_new_vids: bool
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
