import sqlite3
from datetime import datetime
from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Any, Literal

from pydantic import ValidationError

from vidsift.features.video_cache.errors import (DBWritingError,
                                                 VCDataValidationError)
from vidsift.models.video import Video
from vidsift.models.video_cache_model import VideoCacheModel


class VideoCacheRepository:
    def __init__(self) -> None:
        self.db_path: Path = Path(Path.home() / ".local" / "share" / "vidsift" / "processed_videos.db")
        self.conn: Connection = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cur: Cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self) -> None:
        self.cur.execute("""CREATE TABLE IF NOT EXISTS processed_videos (
            video_id TEXT PRIMARY KEY, 
            title TEXT, 
            author TEXT, 
            channel_id TEXT, 
            decision TEXT,
            quality_score FLOAT,
            topic_match_score FLOAT,
            reason TEXT,
            processed_at DATETIME
        )
        """)
        self.conn.commit()

    def save(self,
                vid: Video, 
                channel_id: str, 
                decision: Literal["downloaded", "summarized", "discarded"],
                quality_score: float,
                topic_match_score: float,
                reason: str
                ) -> None:
        """
        Method to save a video to the processed_videos DB, so that it does not get processed again
        """


        try:
            data_as_dict: dict = {
                "video_id": vid.video_id,
                "title": vid.title,
                "author": vid.author,
                "channel_id": channel_id,
                "decision": decision,
                "quality_score": quality_score,
                "topic_match_score": topic_match_score,
                "reason": reason,
                "processed_at": datetime.now()
            }
            try:
                data = VideoCacheModel.model_validate(data_as_dict)
            except ValidationError as e:
                raise VCDataValidationError(f"Data given {data_as_dict} is likely false, validator rejected it: {str(e)}") from e

            self.cur.execute(f"""
            INSERT INTO processed_videos VALUES
            ('{data.video_id}', '{data.title}', '{data.author}', '{data.channel_id}', '{data.decision}', {data.quality_score}, {data.topic_match_score}, '{data.reason}', '{data.processed_at}')""")
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise DBWritingError(f"Failed to write to DB because a database operand violated a constraint: {str(e)}") from e

    def get(self, video_id: str) -> VideoCacheModel | None:
        """
        Method to get the DB entry of the video with the video id video_id.
        """
        row = self.cur.execute(
                f"SELECT * FROM processed_videos WHERE video_id='{video_id}'"
            ).fetchone()
        if row is None:
            return
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
        if (self.cur.execute(f"SELECT * FROM processed_videos WHERE video_id='{video_id}'")).fetchone():
            return True
        else:
            return False

    def close(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    vcr = VideoCacheRepository()
    vid: Video = Video(
            title="sometitle", url="someurl", author="randomauthor", published="someday", video_id="ad90a7d"
    )
    vcr.save(vid=vid, channel_id="alsdjaöldjöasjdöafs", decision="discarded", quality_score=4.0, topic_match_score=5.0, reason="somereason")

    print(vcr.get("ad90a7d"))
