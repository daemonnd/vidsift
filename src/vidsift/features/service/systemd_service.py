import subprocess
from pathlib import Path
from subprocess import CalledProcessError

from platformdirs import user_bin_dir, user_config_dir

from vidsift.features.service.base import VidsiftService
from vidsift.features.service.errors import ServiceError


class SystemdService(VidsiftService):
    def __init__(self) -> None:
        super().__init__()
        self.systemd_user_dir: Path = Path(user_config_dir("systemd")) / "user"
        self.systemd_user_dir.mkdir(parents=True, exist_ok=True)

        self.service_path = self.systemd_user_dir / "vidsift.service"

        self.vidsift_bin_path: Path = Path(user_bin_dir())
        self.vidsift_bin_path.mkdir(parents=True, exist_ok=True)
        self.vidsift_bin_path: Path = self.vidsift_bin_path / "vidsift"
    def install_service(self) -> None:
        self.service_path.touch(exist_ok=True)
        service_contents: str = f"""
[Unit]
Description=Vidsift YouTube pipeline service

[Service]
Type=simple
ExecStart={self.vidsift_bin_path} schedule
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
"""
        self.service_path.write_text(service_contents)

        try:
            subprocess.run("systemctl --user daemon-reload && systemctl --user enable vidsift.service", shell=True, check=True)
        except CalledProcessError as e:
            raise ServiceError(f"Failed to enable systemd vidsift user service: {str(e)}") from e

    def uninstall_service(self) -> None:
        try:
            subprocess.run("systemctl --user daemon-reload && systemctl --user disable --now vidsift.service", shell=True, check=True)
        except CalledProcessError as e:
            raise ServiceError(f"Failed to disable systemd vidsift user service: {str(e)}") from e
        if self.service_path.is_file():
            self.service_path.unlink()
        else:
            raise IsADirectoryError(f"Cannot remove {self.service_path}, because it is a directory")

    def start_service(self) -> None:
        try:
            subprocess.run(["systemctl", "--user", "start", "vidsift.service"], check=True)
        except CalledProcessError as e:
            raise ServiceError(f"Failed to start systemd vidsift user service: {str(e)}") from e

    def stop_service(self) -> None:
        try:
            subprocess.run(["systemctl", "--user", "stop", "vidsift.service"], check=True)
        except CalledProcessError as e:
            raise ServiceError(f"Failed to stop systemd vidsift user service: {str(e)}") from e

    def restart_service(self) -> None:
        try:
            subprocess.run(["systemctl", "--user", "restart", "vidsift.service"], check=True)
        except CalledProcessError as e:
            raise ServiceError(f"Failed to restart systemd vidsift user service: {str(e)}") from e


    def get_status(self) -> str:
        # no check, can exit with non 0 if the service is inactive or failed, which don't didicate failures of the status getting
        result =  subprocess.run(["systemctl", "--user", "status", "vidsift.service"], capture_output=True, text=True)
        return f"{result.stdout}\n{result.stderr}"

