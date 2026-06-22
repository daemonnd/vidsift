import datetime
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor, OperationalError
from time import sleep
from typing import Literal

from platformdirs import user_data_dir

from vidsift.runtime.errors import LockWritingError


class LockManager:
    def __init__(
        self,
        owner: Literal["scheduler", "manual"],
        sleep_interval: float,
        db_path: Path = Path(
            user_data_dir(
                appname="vidsift"
            )
        ) / "lock.db"
    ) -> None:
        self.sleep_interval = sleep_interval
        self.db_path: Path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Connection = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cur: Cursor = self.conn.cursor()
        self._initialize_database(owner=owner)

    def _initialize_database(self, owner) -> None:
        try:
            self.cur.execute("""CREATE TABLE IF NOT EXISTS lock (
                id TEXT PRIMARY KEY,

                owner TEXT,
                status TEXT NOT NULL,
                updated_at TEXT
            )
            """)
            self.cur.execute("""
                INSERT OR IGNORE INTO lock VALUES
                (?, ?, ?, ?)
            """, ("global", owner, "FREE", datetime.datetime.now().isoformat()))
            self.conn.commit()
        except OperationalError as e:
            raise LockWritingError(f"Failed to write to the lock db because of an operational error: {str(e)}") from e




    def acquire(self, owner: Literal["scheduler", "manual"]) -> None:
        """
        Method to acquire the lock
        Waits until lock is free
        """
        first_run: bool = True
        while True:
            try:
                cur = self.conn.execute(
                    """
                    UPDATE lock
                    SET owner = ?,
                        status = 'RUNNING',
                        updated_at = ?
                    WHERE id = 'global'
                    AND status = 'FREE'
                    """,
                    (owner, datetime.datetime.now().isoformat())
                )

                self.conn.commit()
            except OperationalError as e:
                raise LockWritingError(f"Failed to write to the lock db because of an operational error: {str(e)}") from e

            if cur.rowcount == 1:
                return  # lock acquired

            if first_run:
                print(f"""
                If you are sure that no other instance of vidsift is running, 
                then you can remove the lock file using this command:
                ```
                rm {self.db_path}
                ```
                """)
                first_run = False
            sleep(self.sleep_interval)


    def release(self, owner: Literal["scheduler", "manual"]) -> None:
        try:
            self.cur.execute("""
                UPDATE lock
                SET owner = NULL,
                    status = 'FREE',
                    updated_at = ?
                WHERE id = 'global' AND owner = ?
            """, (datetime.datetime.now().isoformat(), owner))
            self.conn.commit()
        except OperationalError as e:
            raise LockWritingError(f"Failed to write to the lock db because of an operational error: {str(e)}") from e

    def close(self) -> None:
        self.conn.close()
