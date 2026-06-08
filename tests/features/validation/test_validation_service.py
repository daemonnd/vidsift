import pytest

from vidsift.models.video import Video
from vidsift.services.validation_service import VideoValidator


@pytest.fixture
def set_up_validator():
    return VideoValidator()

# test data

# each one has 3 levels: a lot, medium, none or almost none of the signal
# Level 1:
#   A lot of that signal
# Level 2:
#   A moderate amount of that signal, but not enough to be a clear signal
# Level 3:
#   A low amount of that signal, or none at all, not enough to be a signal


# placeholder for url, author, published, video_id
fake: str = ""

fvid1 = Video("This is a test video title", fake, fake, fake, fake, fake)
ftranscript1 = "This is a test transcript for the video. It contains multiple sentences and various words to test the pre-validation features."

fvid_emoji_1 = Video("This is a video with 😀😀😀😀😀😀😀", fake, fake, fake, fake, fake)
fvid_emoji_2 = Video("This is a test video title with some emojis 😀😀", fake, fake, fake, fake, fake)
fvid_emoji_3 = Video("This is a test video title with one emoji 😀", fake, fake, fake, fake, fake)

fvid_clickbait_1 = Video("You won't believe what happened next! This is 100% not clickbait, easy money and FREE!", fake, fake, fake, fake, fake)
fvid_clickbait_2 = Video("This containse some clickbait phrases but not all of them, trust me", fake, fake, fake, fake, fake)
fvid_clickbait_3 = Video("This is a clickbait title with some clickbait phrases but not all of them, trust me", fake, fake, fake, fake, fake)

fvid_uppercase_1 = Video("THIS IS A TEST VIDEO TITLE IN UPPERCASE", fake, fake, fake, fake, fake)
fvid_uppercase_2 = Video("This is a Test Video Title with Some Uppercase Words", fake, fake, fake, fake, fake)
fivid_uppercase_3 = Video("This is a test video title in lowercase", fake, fake, fake, fake, fake)

fvid_ponctuation_1 = Video("This is a ??!!!punc!uat!on!!!....", fake, fake, fake, fake, fake)
fvid_ponctuation_2 = Video("This is a test video title with some punctuation!?", fake, fake, fake, fake, fake)
fvid_ponctuation_3 = Video("This is a test video title with no punctuation", fake, fake, fake, fake, fake)

ftransctipt_clickbait_1 = """You won't believe what happened next! This is not clickbait!, 
trust me, that hack is insane and urgent, before we continue, smash that like button and subscribe for more content 
like this, and this is 100% not clickbait"""
ftransctipt_clickbait_2 = "This transcript contains some clickbait phrases but not all of them, trust me"
ftransctipt_clickbait_3 = "This is a transcript with no phrases at all"

fvid_mixed_signals = Video("This is a video with CLICKBAIT but not all of them, trust me, and some emojis 😀😀!!!!", fake, fake, fake, fake, fake)
ftranscript_mixed_signals1 = "This transcript contains some clickbait phrases but not all of them, trust me, and some emojis "
fvid_mixed_signals2 = Video("This is a test video title with some CLICKBAIT phrases but not all of them, trust me, and some emojis 😀😀", fake, fake, fake, fake, fake)
ftranscript_mixed_signals2 = "This transcript contains some clickbait phrases but not all of them, trust me, and some emojis "
# low clickbait signal
fvid_mixed_signals3 = Video("This is a test video title with some CLICKBAIT phrases but not all of them, trust me, and some emojis 😀😀", fake, fake, fake, fake, fake)
ftranscript_mixed_signals3 = "This transcript contains some clickbait phrases but not all of them, trust me, and some emojis "

fvid_short_title = Video("Short", fake, fake, fake, fake, fake)



def test_pre_validation(set_up_validator):
    # normal video
    assert set_up_validator.pre_validate(fvid1, ftranscript1)

    # emoji signal
    assert not set_up_validator.pre_validate(fvid_emoji_1, ftranscript1)
    assert set_up_validator.pre_validate(fvid_emoji_2, ftranscript1)
    assert set_up_validator.pre_validate(fvid_emoji_3, ftranscript1)

    # title clickbait phrases signal
    assert not set_up_validator.pre_validate(fvid_clickbait_1, ftranscript1)
    assert set_up_validator.pre_validate(fvid_clickbait_2, ftranscript1)
    assert set_up_validator.pre_validate(fvid_clickbait_3, ftranscript1)

    # title uppercase signal
    assert not set_up_validator.pre_validate(fvid_uppercase_1, ftranscript1)
    assert set_up_validator.pre_validate(fvid_uppercase_2, ftranscript1)
    assert set_up_validator.pre_validate(fivid_uppercase_3, ftranscript1)

    # ponctuation signal
    assert not set_up_validator.pre_validate(fvid_ponctuation_1, ftranscript1)
    assert set_up_validator.pre_validate(fvid_ponctuation_2, ftranscript1)
    assert set_up_validator.pre_validate(fvid_ponctuation_3, ftranscript1)

    # transcript clickbait phrases signal
    assert not set_up_validator.pre_validate(fvid1, ftransctipt_clickbait_1)
    assert set_up_validator.pre_validate(fvid1, ftransctipt_clickbait_2)
    assert set_up_validator.pre_validate(fvid1, ftransctipt_clickbait_3)

    # short title edge case
    assert set_up_validator.pre_validate(fvid_short_title, ftranscript1)
