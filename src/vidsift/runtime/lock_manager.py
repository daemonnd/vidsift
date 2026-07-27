import json
import os
import socket
import time
from pathlib import Path
from time import sleep
from uuid import UUID

import psutil
from portalocker import Lock, LockException

from vidsift.runtime.errors import LockWritingError
from vidsift.shared.json_utils import normalize
from vidsift.shared.paths import LOCK_FILE_PATH


class LockManager:
    def __init__(
        self, sleep_interval: float, lock_file_path: Path = LOCK_FILE_PATH
    ) -> None:
        self.sleep_interval = sleep_interval
        self.lock_file_path: Path = lock_file_path
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)

        self.lock = Lock(self.lock_file_path)
        self.pid: int = os.getpid()
        self.hostname: str = socket.gethostname()

    def acquire(self, run_id: UUID) -> None:
        """
        Method to acquire the lock
        Waits until lock is free
        """
        first_run = True
        while True:
            try:
                self.lock.acquire()
                fh = self.lock.fh
                fh.seek(0)
                fh.truncate()
                fh.write(
                    json.dumps(
                        normalize(
                            {
                                "pid": self.pid,
                                "process_start_time": psutil.Process(
                                    self.pid
                                ).create_time(),
                                "run_start_time": time.time(),
                                "hostname": self.hostname,
                                "run_id": run_id,
                            }
                        )
                    )
                )
                fh.flush()

            except LockException:
                if first_run:
                    print("""
                        Another vidsift instance is currently running.
                        Waiting for lock release...
                    """)
                    first_run = False
                sleep(self.sleep_interval)
            except (PermissionError, FileNotFoundError) as e:
                raise LockWritingError(str(e))
            else:
                return

    def release(self) -> None:
        self.lock.release()

    # def close(self) -> None:
    # self.lock.release()
