from pathlib import Path
from platformdirs import user_config_dir, user_bin_dir, user_data_dir, user_log_dir

# log paths
VIDSIFT_LOG_DIR: Path = Path(user_log_dir("vidsift"))
VIDSIFT_LOG_FILE: Path = VIDSIFT_LOG_DIR / "vidsift.jsonl"

# data paths
VIDSIFT_DATA_DIR: Path = Path(user_data_dir("vidsift"))
PROCESSED_VIDEOS_DB: Path = VIDSIFT_DATA_DIR / "processed_videos.db"
LOCK_FILE_PATH: Path = VIDSIFT_DATA_DIR / "vidsift.lock"

# bin paths
USER_BIN_DIR: Path = Path(user_bin_dir())
# linux
LINUX_BIN_PATH: Path = USER_BIN_DIR / "vidsift"

# windows
WIN_BIN_PATH: Path = USER_BIN_DIR / "vidsift.exe"

# config paths
VIDSIFT_CONFIG_DIR: Path = Path(user_config_dir("vidsift"))
VIDSIFT_CONFIG_PROMPTS_DIR: Path = VIDSIFT_CONFIG_DIR / "system_prompts"
VIDSIFT_CONFIG_CHANNEL_INSTR_DIR: Path = (
    VIDSIFT_CONFIG_DIR / "custom_channel_instructions"
)
VIDSIFT_CONFIG_FILE_PATH: Path = VIDSIFT_CONFIG_DIR / "config.toml"

# systemd service
SYSTEMD_USER_CONFIG_DIR: Path = Path(user_config_dir("systemd")) / "user"
SYSTEMD_SERVICE_PATH: Path = SYSTEMD_USER_CONFIG_DIR / "vidsift.service"
