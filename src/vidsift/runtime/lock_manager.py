from pathlib import Path
from time import sleep

from platformdirs import user_data_dir
from portalocker import Lock, LockException

from vidsift.runtime.errors import LockWritingError


class LockManager:
    def __init__(
        self,
        sleep_interval: float,
        lock_file_path: Path = Path(
            user_data_dir(
                appname="vidsift"
            )
        ) / "vidsift.lock"
    ) -> None:
        self.sleep_interval = sleep_interval
        self.lock_file_path: Path = lock_file_path
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)



    def acquire(self) -> None:
        """
        Method to acquire the lock
        Waits until lock is free
        """
        first_run = True
        self.lock = Lock(self.lock_file_path)
        while True:
            try:
                self.lock.acquire()
            except LockException:
                if first_run:
                    print("""
                        Another vidsift instance is currently running.
                        Waiting for lock release...
                    """)
                    first_run = False
                sleep(self.sleep_interval)
            else:
                return



    def release(self) -> None:
        self.lock.release()

    # def close(self) -> None:
    # self.lock.release()
