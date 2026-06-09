""" 
    File for validating the video based on rules, if they apply, no AI will be used:
    - all caps
    - a log of emojis
    - known clickbait phrases
"""

import logging
import re

import emoji

from vidsift.features.validation.known_clickbait_phrases import (
    CLICKBAIT_TITLE_PHRASES, CLICKBAIT_TRANSCRIPT_PHRASES)
from vidsift.models.validation.pre_validation_result import PreValidationResult
from vidsift.models.video import Video

logger = logging.getLogger(__name__)




class PreValidator:
    def __init__(self) -> None:
        self.compiled_title_patterns: list[re.Pattern[str]] = []
        for pattern in CLICKBAIT_TITLE_PHRASES:
            lower_pattern: str = pattern.casefold()
            escaped_pattern = re.escape(lower_pattern)
            word_boundary_pattern = rf"\b{escaped_pattern}\b"
            self.compiled_title_patterns.append(re.compile(word_boundary_pattern))

        self.compiled_transcript_patterns: list[re.Pattern[str]] = []
        for pattern in CLICKBAIT_TRANSCRIPT_PHRASES:
            lower_pattern: str = pattern.casefold()
            escaped_pattern = re.escape(lower_pattern)
            word_boundary_pattern = rf"\b{escaped_pattern}\b"
            self.compiled_transcript_patterns.append(re.compile(word_boundary_pattern))


    def get_title_uppercase_ratio(self, title: str) -> float:
        """
        get the title uppercase ratio (the number of uppercase chars devided by the number of letters)
        """
        letters = [c for c in title if c.isalpha()]
        uppercase = [c for c in letters if c.isupper()]
        return len(uppercase) / max(len(letters), 1)

    def get_title_punctuation_ratio(self, title: str) -> float:
        punctuations: int = 0
        for c in title:
            if c in [".", "!", "?"]:
                punctuations += 1

        return punctuations / max(len(title), 1)


    def get_emoji_ratio(self, title: str) -> float:
        """
        get the amount of emojis used in the title
        Returns:
        - ratio of emojis per title characters
        """
        logger.debug(f"Emoji list of title {title}: {emoji.emoji_list(title)}")
        return emoji.emoji_count(title) / max(len(title), 1)

    def get_title_clickbait_phrase_ratio(self, title: str):
        """
        Check how many known clickbait phrases there are int the video/title
        Returns:
        number of founds in title number of findings in transcript / number of words in title
        """

        lower_title: str = title.casefold()

        clickbait_count: int = 0

        for compiled_pattern in self.compiled_title_patterns:
            if compiled_pattern.search(lower_title):
                clickbait_count += 1

        print(f"Title clickbait count: {clickbait_count}, title word count: {len(title.split())}, ratio: {clickbait_count / max(len(title.split()), 1)}")
        return clickbait_count / max(len(title.split()), 1)

    def get_transcript_clickbait_phrase_ratio(self, transcript: str) -> float:
        """
        Check how many known clickbait phrases there are int the video/transcript
        Returns:
        number of founds in title number of findings in transcript / number of words in transcript
        """

        lower_transcript: str = transcript.casefold()

        clickbait_count: int = 0

        for compiled_pattern in self.compiled_transcript_patterns:
            if compiled_pattern.search(lower_transcript):
                clickbait_count += 1

        print(f"Transcript clickbait count: {clickbait_count}, transcript word count: {len(transcript.split())}, ratio: {clickbait_count / max(len(transcript.split()), 1)}")
        return clickbait_count / max(len(transcript.split()), 1)

    def build_pre_validation_features(self, vid: Video, transcript: str) -> PreValidationResult:
        """
        Build the pre validation features for the video
        Returns:
        a PreValidationResult object containing the pre validation features for the video
        """

        return PreValidationResult(
            title_uppercase_ratio=self.get_title_uppercase_ratio(vid.title),
            title_punctuation_ratio=self.get_title_punctuation_ratio(vid.title),
            title_emoji_ratio=self.get_emoji_ratio(vid.title),
            title_clickbait_ratio=self.get_title_clickbait_phrase_ratio(vid.title),
            transcript_clickbait_ratio=self.get_transcript_clickbait_phrase_ratio(transcript)
        )





if __name__ == "__main__":
    vid: Video = Video(
        title="100% percent 😀viral, !!!! like REALLY easy money",
        url="asldl", author="lasjdl", published="lajsdl", video_id="lsydjslafdj")
    transcript: str = "This is a transcript with clickbait phrases like you won't believe what happened next and this is not clickbait"
    pv = PreValidator()
    print(pv.build_pre_validation_features(vid, transcript))


