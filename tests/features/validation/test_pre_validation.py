from pathlib import Path

import pytest

from vidsift.features.validation.pre_validation.metrics_counter import \
    PreValidator
from vidsift.models.video import Video


@pytest.fixture()
def set_up_validator():
    return PreValidator()

# r = real vid
rvid1: Video = Video(title='Summer of CCNA - 90 Minute - Session 2', url='https://www.youtube.com/watch?v=GVlq6lATZ2M', author='NetworkChuck', published='2026-05-21T22:48:57+00:00', video_id='GVlq6lATZ2M')
with open(Path(Path(__file__).parent.parent.parent.parent / "test_data/test_transcript1.txt"), "r") as f:
    rtranscript1: str = f.read()
rvid2: Video = Video(title='you need to use Hermes RIGHT NOW!! (goodbye OpenClaw!!)', url='https://www.youtube.com/watch?v=QQEgIo4Juxg', author='NetworkChuck', published='2026-05-20T16:20:21+00:00', video_id='QQEgIo4Juxg')
with open(Path(Path(__file__).parent.parent.parent.parent / "test_data/test_transcript2.txt"), "r") as f:
    rtranscript2: str = f.read()
rvid3: Video = Video(title="i didn't want to like this....", url='https://www.youtube.com/watch?v=G3jvn7n-68Y', author='NetworkChuck', published='2026-04-09T14:25:50+00:00', video_id='G3jvn7n-68Y')
rvid4: Video = Video(title='the WORST hack of 2026', url='https://www.youtube.com/watch?v=eGSsoSEppNU', author='NetworkChuck', published='2026-03-31T15:00:51+00:00', video_id='eGSsoSEppNU')

# =========================================================
# FAKE TEST VIDEOS
# =========================================================

# f = fake vid

fake: str = "fake"

# -------------------------
# CLEAN / SHOULD MOSTLY PASS
# -------------------------

fvid_clean_1 = Video(
    title="Building a Simple Python CLI with argparse",
    url=fake,
    author="TechBuilder",
    published=fake,
    video_id=fake,
)

ftranscript_clean_1 = """
Today we build a small CLI utility using argparse.
We will structure the parser first and then add subcommands.
Finally we test the behavior manually.
"""

fvid_clean_2 = Video(
    title="Understanding Linux File Permissions",
    url=fake,
    author="SysLab",
    published=fake,
    video_id=fake,
)

ftranscript_clean_2 = """
In this video we look at chmod, ownership and permission groups.
We also explain why recursive chmod operations can become dangerous.
"""

# -------------------------
# TITLE CLICKBAIT
# -------------------------

fvid_clickbait_1 = Video(
    title="THIS CHANGES EVERYTHING!!",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

ftranscript_clickbait_1 = """
Today we compare two database approaches.
The implementation itself is fairly simple.
"""

fvid_clickbait_2 = Video(
    title="You NEED to learn Docker RIGHT NOW!!",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

ftranscript_clickbait_2 = """
We create a basic Docker container and expose a port.
"""

fvid_clickbait_3 = Video(
    title="100% GUARANTEED Python HACK!!",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

ftranscript_clickbait_3 = """
This is a short explanation of decorators and wrappers.
"""

# -------------------------
# TRANSCRIPT CLICKBAIT
# -------------------------

fvid_transcript_1 = Video(
    title="Python Logging Basics",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

ftranscript_transcript_1 = """
Before we continue, smash that like button.
This changes everything.
Stay tuned because you won't believe what happened.
"""

fvid_transcript_2 = Video(
    title="Intro to Bash Scripting",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

ftranscript_transcript_2 = """
This simple hack will save you hours.
Trust me.
Almost nobody knows this.
Act now before everyone else does.
"""

# -------------------------
# EMOJI EDGE CASES
# -------------------------

fvid_emoji_1 = Video(
    title="😀😀😀 FASTEST PYTHON TRICK 😀😀😀",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

fvid_emoji_2 = Video(
    title="Python Tips 👍",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

fvid_emoji_3 = Video(
    title="normal title without emojis",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

# -------------------------
# UPPERCASE EDGE CASES
# -------------------------

fvid_uppercase_1 = Video(
    title="THIS IS ALL UPPERCASE",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

fvid_uppercase_2 = Video(
    title="This Has SOME Upp",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

fvid_uppercase_3 = Video(
    title="lowercase only title",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

fvid_uppercase_4 = Video(
    title="MIXED Case TITLE with SOME UPPER and some lower",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

# -------------------------
# BORDERLINE / FALSE POSITIVE TESTS
# -------------------------

fvid_borderline_1 = Video(
    title="Massive Update on Python Packaging",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

# contains "massive update" but is not really clickbait

ftranscript_borderline_1 = """
Today we discuss the latest packaging ecosystem changes.
"""

fvid_borderline_2 = Video(
    title="Network Protocol Warning Systems",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

# contains "warning"

ftranscript_borderline_2 = """
This lecture explains warning propagation in distributed systems.
"""

# -------------------------
# MIXED SIGNAL TESTS
# -------------------------

fvid_mixed_1 = Video(
    title="Docker Networking Explained",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

ftranscript_mixed_1 = """
You need to see this.
This changes the game.
But first we explain bridge networking fundamentals.
"""

fvid_mixed_2 = Video(
    title="THIS is why Linux matters!!",
    url=fake,
    author=fake,
    published=fake,
    video_id=fake,
)

ftranscript_mixed_2 = """
Today we explain Linux namespaces and process isolation.
No clickbait here after the intro.
"""

# -------------------------
# Full of one signal but not the other
# --------------------------
fvid_full_signal_1 = Video(
    title="...!!!?????", url=fake, author=fake, published=fake, video_id=fake)
fvid_full_signal_2 = Video(
    title="😀⌛🏘️📅🔥❗", url=fake, author=fake, published=fake, video_id=fake)




def test_get_title_uppercase_ratio(set_up_validator):
    pre_validator: PreValidator = set_up_validator
    assert pre_validator.get_title_uppercase_ratio(rvid1.title) == 0.28
    assert pre_validator.get_title_uppercase_ratio(fvid_emoji_3.title) == 0.0
    assert pre_validator.get_title_uppercase_ratio(fvid_uppercase_1.title) == 1.0
    assert pre_validator.get_title_uppercase_ratio(fvid_uppercase_2.title) == 0.5
    assert pre_validator.get_title_uppercase_ratio(fvid_uppercase_3.title) == 0.0
    assert pre_validator.get_title_uppercase_ratio(fvid_uppercase_4.title) == 0.5128205128205128
    assert pre_validator.get_title_uppercase_ratio(fvid_borderline_2.title) == 0.13793103448275862
    assert pre_validator.get_title_uppercase_ratio(fvid_full_signal_1.title) == 0.0

def test_get_title_punctuation_ratio(set_up_validator):
    pre_validator: PreValidator = set_up_validator
    assert pre_validator.get_title_punctuation_ratio(rvid1.title) == 0.0
    assert pre_validator.get_title_punctuation_ratio(fvid_emoji_3.title) == 0.0
    assert pre_validator.get_title_punctuation_ratio(fvid_clickbait_1.title) == 0.08
    assert pre_validator.get_title_punctuation_ratio(fvid_clickbait_3.title) == 0.06896551724137931
    assert pre_validator.get_title_punctuation_ratio(fvid_borderline_1.title) == 0.0
    assert pre_validator.get_title_punctuation_ratio(fvid_full_signal_1.title) == 1.0

def test_get_emoji_ratio(set_up_validator):
    pre_validator: PreValidator = set_up_validator
    assert pre_validator.get_emoji_ratio(rvid1.title) == 0.0
    assert pre_validator.get_emoji_ratio(fvid_emoji_1.title) ==  0.21428571428571427
    assert pre_validator.get_emoji_ratio(fvid_emoji_2.title) ==  0.07692307692307693
    assert pre_validator.get_emoji_ratio(fvid_emoji_3.title) == 0.0
    assert pre_validator.get_emoji_ratio(fvid_full_signal_2.title) == 0.8571428571428571

def test_get_title_clickbait_phrase_ratio(set_up_validator):
    pre_validator: PreValidator = set_up_validator
    assert pre_validator.get_title_clickbait_phrase_ratio(rvid1.title) == 0
    assert pre_validator.get_title_clickbait_phrase_ratio(fvid_clickbait_1.title) == 0.3333333333333333
    assert pre_validator.get_title_clickbait_phrase_ratio(fvid_clickbait_2.title) == 0
    assert pre_validator.get_title_clickbait_phrase_ratio(fvid_clickbait_3.title) == 0.5
    assert pre_validator.get_title_clickbait_phrase_ratio(fvid_borderline_1.title) == 0.2
    assert pre_validator.get_title_clickbait_phrase_ratio(fvid_full_signal_1.title) == 0

def test_get_transcript_clickbait_phrase_ratio(set_up_validator):
    pre_validator: PreValidator = set_up_validator
    assert pre_validator.get_transcript_clickbait_phrase_ratio(rtranscript1) == 0.0004369356248179435
    assert pre_validator.get_transcript_clickbait_phrase_ratio(rtranscript2) == 0
    assert pre_validator.get_transcript_clickbait_phrase_ratio(ftranscript_clean_1) == 0
    assert pre_validator.get_transcript_clickbait_phrase_ratio(ftranscript_clean_2) == 0
    assert pre_validator.get_transcript_clickbait_phrase_ratio(ftranscript_transcript_1) == 0.2777777777777778

