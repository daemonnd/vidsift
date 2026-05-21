""" 
    File for validating the video based on rules, if they apply, no AI will be used:
    - all caps
    - a log of emojis
    - known clickbait phrases
"""

from typing import Tuple

import emoji

from vidsift.features.validation.known_clickbait_phrases import (
    CLICKBAIT_TITLE_PHRASES, CLICKBAIT_TRANSCRIPT_PHRASES)
from vidsift.models.video import Video


class PreValidator:
    def __init__(self) -> None:
        pass

    def check_title(self, title: str) -> int:
        """
        Check the video title
        If more than half of the characters are emojis/uppercase, it the number of bad signs in the title
        """
        if title.isupper():
            return len(title)

        truth_list: list[bool] = []
        for char in title:
            if char.isupper():
                truth_list.append(False)
                continue

            if emoji.emoji_list(char):
                truth_list.append(False)
                continue
            truth_list.append(True)

        bad_signs: int = 0
        for element in truth_list:
            if not element:
                bad_signs += 1
        return bad_signs





    def check_clickbait_phrases(self, title: str, transcript: str) -> Tuple[int, int]:
        """
        Check how many known clickbait phrases there are int the video/title
        Returns:
        number of founds in title number of findings in transcript
        """

        title_clickbait_count: int = 0
        transcript_clickbait_count: int = 0

        # title
        for clickbait_title_phrase in CLICKBAIT_TITLE_PHRASES:
            if clickbait_title_phrase.lower() in title.lower():
                title_clickbait_count += 1

        # transcript
        for clickbait_transcript_phrase in CLICKBAIT_TRANSCRIPT_PHRASES:
            if clickbait_transcript_phrase.lower() in transcript.lower():
                transcript_clickbait_count += 1
        return title_clickbait_count, transcript_clickbait_count




if __name__ == "__main__":
    vid: Video = Video(
        title="100% percent viral, !!!! like really",
        url="asldl", author="lasjdl", published="lajsdl", video_id="lsydjslafdj")
    transcript: str = "this is a very urgent cause"
    pv = PreValidator()
    print(pv.check_clickbait_phrases(title=vid.title, transcript=transcript))


