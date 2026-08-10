import subprocess


from vidsift.features.service.base import VidsiftService
from vidsift.features.service.errors import ServiceExecutionError
from vidsift.shared.paths import WIN_BIN_PATH


class SchtasksService(VidsiftService):
    TASK_NAME = "vidsift"

    def install_service(self) -> None:
        vidsift_path = rf'"{WIN_BIN_PATH}" schedule'

        try:
            subprocess.run(
                [
                    "schtasks",
                    "/Create",
                    "/TN",
                    self.TASK_NAME,
                    "/TR",
                    vidsift_path,
                    "/SC",
                    "ONLOGON",
                    "/F",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ServiceExecutionError(f"Failed to install service: {e}") from e

    def uninstall_service(self) -> None:
        try:
            subprocess.run(
                [
                    "schtasks",
                    "/Delete",
                    "/TN",
                    self.TASK_NAME,
                    "/F",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ServiceExecutionError(f"Failed to uninstall service: {e}") from e

    def start_service(self) -> None:
        try:
            subprocess.run(
                [
                    "schtasks",
                    "/Run",
                    "/TN",
                    self.TASK_NAME,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ServiceExecutionError(f"Failed to start service: {e}") from e

    def stop_service(self) -> None:
        try:
            subprocess.run(
                [
                    "schtasks",
                    "/End",
                    "/TN",
                    self.TASK_NAME,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ServiceExecutionError(f"Failed to stop service: {e}") from e

    def restart_service(self) -> None:
        try:
            subprocess.run(
                [
                    "schtasks",
                    "/End",
                    "/TN",
                    self.TASK_NAME,
                ],
                check=True,
            )

            subprocess.run(
                [
                    "schtasks",
                    "/Run",
                    "/TN",
                    self.TASK_NAME,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ServiceExecutionError(f"Failed to restart service: {e}") from e

    def get_status(self) -> str | None:
        try:
            result = subprocess.run(
                [
                    "schtasks",
                    "/Query",
                    "/TN",
                    self.TASK_NAME,
                    "/FO",
                    "LIST",
                    "/V",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            try:
                if result:
                    raise ServiceExecutionError(
                        f"Failed to get service status: {e}. STDERR: {result.stderr}"
                    ) from e
            except UnboundLocalError:
                pass
            raise ServiceExecutionError(
                f"Failed to get service status: {e}. STDERR is not availible."
            ) from e
        else:
            return f"{result.stdout}\n{result.stderr}"
