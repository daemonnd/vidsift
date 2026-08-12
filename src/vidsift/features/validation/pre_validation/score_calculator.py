from typing import Tuple

from vidsift.config.models import AppConfig
from vidsift.features.validation.pre_validation.metrics_counter import \
    PreValidator
from vidsift.models.validation.pre_validation_result import PreValidationResult
from vidsift.models.video import Video

METRIC_AMOUNT: int = 5


class PreValidationScoreCalculator:
    def __init__(self, config: AppConfig) -> None:
        self.config: AppConfig = config
        self.weak = self.config.validation.pre_validation.weak
        self.max_allowed = self.config.validation.pre_validation.max_allowed
        self.weights = self.config.validation.pre_validation.weights

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
        sum_all_weights = self.weights.title_emoji_weight + self.weights.title_uppercase_weight + self.weights.title_punctuation_weight + self.weights.transcript_clickbait_weight
        return sum_weak_signals / sum_all_weights, f"{sum_weak_signals} weak signals weight out of {sum_all_weights} total weight which is {sum_weak_signals / sum_all_weights:.2f} score"


    def check_suspicious_metric(self, result: PreValidationResult) -> Tuple[bool, str]:
        """
        Method to check if any of the pre-validation metrics are above the threshold, if so, return True and the reason, otherwise return False and an empty string
        """
        if result.title_uppercase_ratio > self.max_allowed.title_uppercase_ratio:
            return True, f"title_uppercase_ratio is {result.title_uppercase_ratio}, which is above the threshold of 0.4"
        if result.title_punctuation_ratio > self.max_allowed.title_punctuation_ratio:
            return True, f"title_punctuation_ratio is {result.title_punctuation_ratio}, which is above the threshold of 0.1"
        if result.title_clickbait_ratio > self.max_allowed.title_clickbait_ratio:
            return True, f"title_clickbait_ratio is {result.title_clickbait_ratio}, which is above the threshold of 0.15"
        if result.title_emoji_ratio > self.max_allowed.title_emoji_ratio:
            return True, f"title_emoji_ratio is {result.title_emoji_ratio}, which is above the threshold of 0.2"
        if result.transcript_clickbait_ratio > self.max_allowed.transcript_clickbait_ratio:
            return True, f"transcript_clickbait_ratio is {result.transcript_clickbait_ratio}, which is above the threshold of 0.1"
        return False, ""

    def get_weak_signals(self, result: PreValidationResult) -> list[float]:
        """
        Method to check if any of the pre-validation metrics are above the weak signal threshold,
        if so, return a list of the weak signals, otherwise return an empty list.
        """
        weak_signals: list[float] = []

        weights = self.config.validation.pre_validation.weights

        if result.title_uppercase_ratio > self.weak.title_uppercase_ratio:
            weak_signals.append(weights.title_uppercase_weight)

        if result.title_punctuation_ratio > self.weak.title_punctuation_ratio:
            weak_signals.append(weights.title_punctuation_weight)

        if result.title_clickbait_ratio > self.weak.title_clickbait_ratio:
            weak_signals.append(weights.title_clickbait_weight)

        if result.title_emoji_ratio > self.weak.title_emoji_ratio:
            weak_signals.append(weights.title_emoji_weight)

        if result.transcript_clickbait_ratio > self.weak.transcript_clickbait_ratio:
            weak_signals.append(weights.transcript_clickbait_weight)

        return weak_signals
