import subprocess
from subprocess import CalledProcessError


from vidsift.features.service.base import VidsiftService
from vidsift.features.service.errors import ServiceError
from vidsift.shared.paths import (
    USER_BIN_DIR,
    SYSTEMD_SERVICE_PATH,
    SYSTEMD_USER_CONFIG_DIR,
    LINUX_BIN_PATH,
)


class SystemdService(VidsiftService):
    def __init__(self) -> None:
        super().__init__()
        SYSTEMD_USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        USER_BIN_DIR.mkdir(parents=True, exist_ok=True)

    def install_service(self) -> None:
        SYSTEMD_SERVICE_PATH.touch(exist_ok=True)
        service_contents: str = f"""
[Unit]
Description=Vidsift YouTube pipeline service

[Service]
Type=simple
ExecStart={LINUX_BIN_PATH} schedule
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
"""
        SYSTEMD_SERVICE_PATH.write_text(service_contents)

        try:
            subprocess.run(
                "systemctl --user daemon-reload && systemctl --user enable vidsift.service",
                shell=True,
                check=True,
            )
        except CalledProcessError as e:
            raise ServiceError(
                f"Failed to enable systemd vidsift user service: {str(e)}"
            ) from e

    def uninstall_service(self) -> None:
        try:
            subprocess.run(
                "systemctl --user daemon-reload && systemctl --user disable --now vidsift.service",
                shell=True,
                check=True,
            )
        except CalledProcessError as e:
            raise ServiceError(
                f"Failed to disable systemd vidsift user service: {str(e)}"
            ) from e
        if SYSTEMD_SERVICE_PATH.is_file():
            SYSTEMD_SERVICE_PATH.unlink()
        else:
            raise IsADirectoryError(
                f"Cannot remove {SYSTEMD_SERVICE_PATH}, because it is a directory"
            )

    def start_service(self) -> None:
        try:
            subprocess.run(
                ["systemctl", "--user", "start", "vidsift.service"], check=True
            )
        except CalledProcessError as e:
            raise ServiceError(
                f"Failed to start systemd vidsift user service: {str(e)}"
            ) from e

    def stop_service(self) -> None:
        try:
            subprocess.run(
                ["systemctl", "--user", "stop", "vidsift.service"], check=True
            )
        except CalledProcessError as e:
            raise ServiceError(
                f"Failed to stop systemd vidsift user service: {str(e)}"
            ) from e

    def restart_service(self) -> None:
        try:
            subprocess.run(
                ["systemctl", "--user", "restart", "vidsift.service"], check=True
            )
        except CalledProcessError as e:
            raise ServiceError(
                f"Failed to restart systemd vidsift user service: {str(e)}"
            ) from e

    def get_status(self) -> str:
        # no check, can exit with non 0 if the service is inactive or failed, which don't didicate failures of the status getting
        result = subprocess.run(
            ["systemctl", "--user", "status", "vidsift.service"],
            capture_output=True,
            text=True,
        )
        return f"{result.stdout}\n{result.stderr}"
