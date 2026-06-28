import subprocess
from pathlib import Path

from platformdirs import user_bin_dir, user_config_dir

from vidsift.features.service.base import VidsiftService


class SystemdService(VidsiftService):
    def __init__(self) -> None:
        super().__init__()
        self.service_path: Path = Path(user_config_dir("systemd"))
        self.service_path.mkdir(parents=True, exist_ok=True)
        self.service_path = self.service_path / "user" / "vidsift.service"
        self.service_path.touch(exist_ok=True)

        self.vidsift_bin_path: Path = Path(user_bin_dir())
        self.vidsift_bin_path.mkdir(parents=True, exist_ok=True)
        self.vidsift_bin_path: Path = self.vidsift_bin_path / "vidsift"
    def install_service(self) -> None:
        service_contents: str = f"""
[Unit]
Description=Vidsift YouTube pipeline service

[Service]
Type=simple
ExecStart={self.vidsift_bin_path} schedule
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
"""
        self.service_path.write_text(service_contents)

        subprocess.run("systemctl --user enable vidsift.service && systemctl --user daemon-reload", shell=True)

    def uninstall_service(self) -> None:
        subprocess.run("systemctl --user disable --now vidsift.service && systemctl --user daemon-reload", shell=True)
        if self.service_path.is_file():
            self.service_path.unlink()
        else:
            raise IsADirectoryError(f"Cannot remove {self.service_path}, because it is a directory")

    def start_service(self) -> None:
        subprocess.run("systemctl --user start vidsift.service")
    def stop_service(self) -> None:
        subprocess.run("systemctl --user stop vidsift.service")
    def get_status(self) -> str:
        result =  subprocess.run("systemctl --user status vidsift.service", capture_output=True)
        return result.stdout.decode()
