import platform

from vidsift.features.service.base import VidsiftService
from vidsift.features.service.errors import OSNotSupportedError, ServiceError
from vidsift.features.service.launchd_service import LaunchdService
from vidsift.features.service.systemd_service import SystemdService
from vidsift.features.service.task_scheduler_service import \
    TaskSchedulerService


class BgRunnserService(VidsiftService):
    def __init__(self) -> None:
        super().__init__()
        self.os = platform.system()
        if self.os not in ["Linux", "Darwin", "Windows"]:
            raise OSNotSupportedError(f"The OS {self.os} is not supported for background services")
        match self.os:
            case "Linux":
                self.service: VidsiftService = SystemdService()
            case "Darwin":
                self.service: VidsiftService = LaunchdService()
            case "Windows":
                self.service: VidsiftService = TaskSchedulerService()

    def install_service(self) -> None:
        try:
            self.service.install_service()
        except ServiceError:
            raise
    def uninstall_service(self) -> None:
        try:
            self.service.uninstall_service()
        except ServiceError:
            raise
    def start_service(self) -> None:
        try:
            self.service.start_service()
        except ServiceError:
            raise
    def stop_service(self) -> None:
        try:
            self.service.stop_service()
        except ServiceError:
            raise
    def get_status(self) -> None:
        try:
            self.service.get_status()
        except ServiceError:
            raise
