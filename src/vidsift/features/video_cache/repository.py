import datetime
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor, IntegrityError, OperationalError
from typing import Generator, Literal

from pydantic import ValidationError

from vidsift.features.video_cache.errors import (DBWritingError,
                                                 VCDataValidationError)
from vidsift.models.video import Video
from vidsift.models.video_cache_model import ProcessingStatus, VideoCacheModel


class VideoCacheRepository:
    def __init__(self) -> None:
        self.db_path: Path = Path(Path.home() / ".local" / "share" / "vidsift" / "processed_videos.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Connection = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cur: Cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self) -> None:
        self.cur.execute("""CREATE TABLE IF NOT EXISTS processed_videos (
            video_id TEXT PRIMARY KEY,

            title TEXT NOT NULL, 
            url TEXT NOT NULL,
            author TEXT NOT NULL, 
            channel_id TEXT NOT NULL, 
            published TEXT NOT NULL,

            status TEXT NOT NULL,

            decision TEXT,
            quality_score REAL,
            topic_match_score REAL,
            reason TEXT,

            processed_at TEXT,
            last_error TEXT
        )
        """)
        self.conn.commit()

    def create(self, vid: Video):
        """
        Method for setting the status to VALIDATING after a video got discovered
        """
        try:
            parameters: tuple = (vid.video_id, vid.title, vid.url, vid.author, vid.channel_id, vid.published, ProcessingStatus.VALIDATING.value, None, None, None, None,  None, None)
            self.cur.execute("""
            INSERT INTO processed_videos VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", parameters)
            self.conn.commit()
        except IntegrityError as e:
            raise DBWritingError(f"Failed to write to DB while setting the status to VALIDATING because a database operand violated a constraint: {str(e)}") from e
        except OperationalError as e:
            raise DBWritingError(f"Failed to write to DB while setting the status to VALIDATING because of an operational Error: {str(e)}") from e

    def save_validation_result(self, 
                video_id: str,
                decision: Literal["downloaded", "summarized", "discarded"],
                quality_score: float,
                topic_match_score: float,
                reason: str
            ):
        """
        Method to add the validation data to the table entry and update the status to ether DONE, DOWNLOADING or SUMMARIZING
        """
        try:
            parameters: tuple = (decision, quality_score, topic_match_score, reason, video_id)
            self.cur.execute("""
            UPDATE processed_videos
            SET decision = ?,
            quality_score = ?,
            topic_match_score = ?,
            reason = ?
            WHERE video_id = ?
            """, parameters)
            self.conn.commit()
        except IntegrityError as e:
            raise DBWritingError(f"Failed to write to DB while updating the status after validation because a database operand violated a constraint: {str(e)}") from e
        except OperationalError as e:
            raise DBWritingError(f"Failed to write to DB while updating the status after validation because of an operational Error: {str(e)}") from e

    def update_after_done(self,
                          video_id: str,
                          decision: Literal["downloaded", "summarized", "discarded"]
        ):
        """
        Method to set the status to DONE and mark the video as processed successfully
        """
        try:
            parameters: tuple = (ProcessingStatus.DONE.value, decision, video_id, datetime.datetime.now().isoformat())
            self.cur.execute("""
            UPDATE processed_videos
            SET status = ?,
            decision = ?,
            processed_at = ?
            WHERE video_id = ?
            """, parameters)

            self.conn.commit()

        except IntegrityError as e:
            raise DBWritingError(f"Failed to write to DB while updating the status after the video with id {video_id} has been {decision}, because a database operand violated a constraint: {str(e)}") from e
        except OperationalError as e:
            raise DBWritingError(f"Failed to write to DB while updating the status after the video with id {video_id} has been {decision}, because of an operational Error: {str(e)}") from e


    def mark_failed(self, error_msg: str, video_id: str):
        """
        Method to mart a download / summary / validation as failed, updates last_error and sets the status to FAILED
        """
        try:
            parameters: tuple = (ProcessingStatus.FAILED.value, error_msg, video_id)
            self.cur.execute("""
            UPDATE processed_videos
            SET status = ?,
            last_error = ?
            WHERE video_id = ?
            """, parameters)

            self.conn.commit()

        except IntegrityError as e:
            raise DBWritingError(f"Failed to write to DB while updating the status after validation because a database operand violated a constraint: {str(e)}")
        except OperationalError as e:
            raise DBWritingError(f"Failed to write to DB while updating the status after validation because of an operational Error: {str(e)}") from e

    def get(self, video_id: str) -> VideoCacheModel | None:
        """
        Method to get the DB entry of the video with the video id video_id.
        """
        row = self.cur.execute(
                "SELECT * FROM processed_videos WHERE video_id=?", (video_id,)
            ).fetchone()
        if row is None:
            return None
        try:
            return VideoCacheModel.model_validate(dict(row))
        except ValidationError as e:
            raise VCDataValidationError(f"Failed to return results because of a ValidationError from pydantic: {str(e)}") from e


    def exists(self, video_id: str) -> bool:
        """
        Method to get if an entry already exists
        Returns True if it already exists
        Returns False if it does not exist
        """
        if (self.cur.execute(
            "SELECT 1 FROM processed_videos WHERE video_id=?", (video_id,))
            ).fetchone():
            return True
        else:
            return False

    def get_by_status(self, status: Literal["downloading", "summarizing", "done", "failed", "validating"]) -> Generator[VideoCacheModel, None, None]:
        """
        Method to get a list of the videos interrupted
        """
        parameters: tuple = (status,)
        rows = self.cur.execute("""
        SELECT * FROM processed_videos
        WHERE status = ?
        """, parameters).fetchall()
        if rows is None:
            return None
        for row in rows:
            try:
                yield VideoCacheModel.model_validate(dict(row))
            except ValidationError as e:
                raise VCDataValidationError(f"Failed to get the data of a video because of a ValidationError, database seems corrupt: {str(e)}") from e


    def close(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    vcr = VideoCacheRepository()
    vid: Video = Video(
            title="sometitle", url="someurl", author="randomauthor", published="someday", video_id="ai90a7di7hk", channel_id="somechannelid"
    )

    vcr.create(vid=vid)
    result = vcr.get("ai90a7di7hk")
    print(result)
