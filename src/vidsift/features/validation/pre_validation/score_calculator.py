from typing import Tuple

from vidsift.config.parser import (MAX_ALLOWED_TITLE_CLICKBAIT_RATIO,
                                   MAX_ALLOWED_TITLE_EMOJI_RATIO,
                                   MAX_ALLOWED_TITLE_PUNCTUATION_RATIO,
                                   MAX_ALLOWED_TITLE_UPPERCASE_RATIO,
                                   MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_RATIO,
                                   WEAK_TITLE_CLICKBAIT_RATIO,
                                   WEAK_TITLE_EMOJI_RATIO,
                                   WEAK_TITLE_PUNCTUATION_RATIO,
                                   WEAK_TITLE_UPPERCASE_RATIO,
                                   WEAK_TRANSCRIPT_CLICKBAIT_RATIO,
                                   WEIGHT_TITLE_CLICKBAIT_RATIO,
                                   WEIGHT_TITLE_EMOJI_RATIO,
                                   WEIGHT_TITLE_PUNCTUATION_RATIO,
                                   WEIGHT_TITLE_UPPERCASE_RATIO,
                                   WEIGHT_TRANSCRIPT_CLICKBAIT_RATIO)
from vidsift.features.validation.pre_validation.metrics_counter import \
    PreValidator
from vidsift.models.validation.pre_validation_result import PreValidationResult
from vidsift.models.video import Video

METRIC_AMOUNT: int = 5

class PreValidationScoreCalculator:
    def __init__(self) -> None:
        self.validator: PreValidator = PreValidator()

    def calculate_score(self, result: PreValidationResult) -> Tuple[float, str]:
        """
        Calculate the pre-validation score based on the pre-validation result.
        The score is a value between 0 and 1, where 1 means the video is very likely to be clickbait, and 0 means it is not clickbait.
        """
        suspicious, reason = self.check_suspicious_metric(result)
        if suspicious:
            return 1.0, reason

        weak_signals = self.get_weak_signals(result)
        sum_weak_signals = sum(weak_signals)
        sum_all_weights = WEIGHT_TITLE_EMOJI_RATIO + WEIGHT_TITLE_PUNCTUATION_RATIO + WEIGHT_TITLE_CLICKBAIT_RATIO + WEIGHT_TRANSCRIPT_CLICKBAIT_RATIO
        return sum_weak_signals / sum_all_weights, f"{sum_weak_signals} weak signals weight out of {sum_all_weights} total weight which is {sum_weak_signals / sum_all_weights:.2f} score"



    def check_suspicious_metric(self, result: PreValidationResult) -> Tuple[bool, str]:
        """
        Method to check if any of the pre-validation metrics are above the threshold, if so, return True and the reason, otherwise return False and an empty string
        """
        if result.title_uppercase_ratio > MAX_ALLOWED_TITLE_UPPERCASE_RATIO:
            return True, f"title_uppercase_ratio is {result.title_uppercase_ratio}, which is above the threshold of 0.4"
        if result.title_punctuation_ratio > MAX_ALLOWED_TITLE_PUNCTUATION_RATIO:
            return True, f"title_punctuation_ratio is {result.title_punctuation_ratio}, which is above the threshold of 0.1"
        if result.title_clickbait_ratio > MAX_ALLOWED_TITLE_CLICKBAIT_RATIO:
            return True, f"title_clickbait_ratio is {result.title_clickbait_ratio}, which is above the threshold of 0.15"
        if result.title_emoji_ratio > MAX_ALLOWED_TITLE_EMOJI_RATIO:
            return True, f"title_emoji_ratio is {result.title_emoji_ratio}, which is above the threshold of 0.2"
        if result.transcript_clickbait_ratio > MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_RATIO:
            return True, f"transcript_clickbait_ratio is {result.transcript_clickbait_ratio}, which is above the threshold of 0.1"
        return False, ""

    def get_weak_signals(self, result: PreValidationResult) -> list[float]:
        """
        Method to check if any of the pre-validation metrics are above the weak signal threshold, if so, return a list of the weak signals, otherwise return an empty list
        """
        weak_signals: list[float] = []
        if result.title_uppercase_ratio > WEAK_TITLE_UPPERCASE_RATIO:
            #print(f"title_uppercase_ratio is {result.title_uppercase_ratio}, which is above the weak signal threshold of {WEAK_TITLE_UPPERCASE_RATIO}")
            weak_signals.append(WEIGHT_TITLE_UPPERCASE_RATIO)
        if result.title_punctuation_ratio > WEAK_TITLE_PUNCTUATION_RATIO:
            #print(f"title_punctuation_ratio is {result.title_punctuation_ratio}, which is above the weak signal threshold of {WEAK_TITLE_PUNCTUATION_RATIO}")
            weak_signals.append(WEIGHT_TITLE_PUNCTUATION_RATIO)
        if result.title_clickbait_ratio > WEAK_TITLE_CLICKBAIT_RATIO:
            #print(f"title_clickbait_ratio is {result.title_clickbait_ratio}, which is above the weak signal threshold of {WEAK_TITLE_CLICKBAIT_RATIO}")
            weak_signals.append(WEIGHT_TITLE_CLICKBAIT_RATIO)
        if result.title_emoji_ratio > WEAK_TITLE_EMOJI_RATIO:
            #print(f"title_emoji_ratio is {result.title_emoji_ratio}, which is above the weak signal threshold of {WEAK_TITLE_EMOJI_RATIO}")
            weak_signals.append(WEIGHT_TITLE_EMOJI_RATIO)
        if result.transcript_clickbait_ratio > WEAK_TRANSCRIPT_CLICKBAIT_RATIO:
            #print(f"transcript_clickbait_ratio is {result.transcript_clickbait_ratio}, which is above the weak signal of {WEAK_TRANSCRIPT_CLICKBAIT_RATIO}")
            weak_signals.append(WEIGHT_TRANSCRIPT_CLICKBAIT_RATIO)

        #print(f"Weak signals: {weak_signals}")
        return weak_signals

if __name__ == "__main__":
    result = PreValidationResult(title_uppercase_ratio=0.5, title_punctuation_ratio=0.1, title_clickbait_ratio=2, 
                                 title_emoji_ratio=0.2, transcript_clickbait_ratio=5)
    vid: Video = Video(title="This is a clickbait title guaranteed for free and , so no not miss this!!!", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", author="Rick Astley", published="1987-10-25", video_id="dQw4w9WgXcQ")
    transcript: str = "This is a transcript with clickbait phrases like you won't believe what happened next and this is not clickbait"
    from vidsift.features.validation.pre_validation.metrics_counter import \
        PreValidator
    pv: PreValidator = PreValidator()
    result: PreValidationResult = pv.build_pre_validation_features(vid, transcript)
    pvsc: PreValidationScoreCalculator = PreValidationScoreCalculator()
    print(pvsc.calculate_score(result))

