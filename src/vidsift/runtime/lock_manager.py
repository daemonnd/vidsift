import datetime
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor
from time import sleep
from typing import Literal

from vidsift.runtime.errors import LockingError, MoreThanOneRowError


class LockManager:
    def __init__(self, owner: Literal["scheduler", "manual"], db_path: Path | None = None) -> None:
        if db_path is None:
            self.db_path: Path = Path(Path.home() / ".local" / "share" / "vidsift" / "processed_videos.db")
        else:
            self.db_path: Path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Connection = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cur: Cursor = self.conn.cursor()
        self._initialize_database(owner=owner)

    def _initialize_database(self, owner) -> None:
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




    def acquire(self, owner: Literal["scheduler", "manual"], sleep_interval: float = 10) -> None:
        """
        Method to acquire the lock
        Waits until lock is free
        """
        while True:
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

            if cur.rowcount == 1:
                return  # lock acquired

            sleep(sleep_interval)


    def release(self, owner: Literal["scheduler", "manual"]) -> None:

        self.cur.execute("""
            UPDATE lock
            SET owner = NULL,
                status = 'FREE',
                updated_at = ?
            WHERE id = 'global' AND owner = ?
        """, (datetime.datetime.now().isoformat(), owner))
        self.conn.commit()

