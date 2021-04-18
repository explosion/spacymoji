from spacy.lang.en import English
import pytest
from spacymoji import Emoji


@pytest.fixture(scope="function")
def nlp():
    return English()


def test_integration(nlp):
    nlp.add_pipe("emoji")
    assert nlp.pipe_names[-1] == "emoji"


@pytest.mark.parametrize("icon", ["🐼", "😇", "\U0001F45E"])
def test_usage_single_emoji(nlp, icon):
    nlp.add_pipe("emoji")
    doc = nlp("Hello %s world" % icon)
    assert doc._.has_emoji
    assert doc[1]._.is_emoji
    assert doc[1]._.emoji_desc == nlp.get_pipe("emoji").get_emoji_desc(doc[1])
    assert doc[1:3]._.has_emoji
    assert len(doc._.emoji) == 1
    emoji_text, emoji_idx, emoji_desc = doc._.emoji[0]
    assert emoji_text == icon
    assert emoji_idx == 1


def test_usage_no_emoji(nlp):
    nlp.add_pipe("emoji")
    doc = nlp("In total there are 2,666 emojis in the Unicode Standard.")
    assert not doc._.has_emoji
    for token in doc:
        assert not token._.is_emoji


def test_usage_multiple_emoji(nlp):
    nlp.add_pipe("emoji")
    doc = nlp("Hello 😻🍕 world, this ✨ 💥 is an example.")
    assert doc._.has_emoji
    assert len(doc._.emoji) == 4
    assert doc[:5]._.has_emoji
    assert len(doc[:5]._.emoji) == 2


@pytest.mark.parametrize("emoji", ["👌🏾", "👩‍💻", "\U0001F933\U0001F3FD"])
def test_usage_merge_spans(nlp, emoji):
    text = "This is %s a test" % emoji
    doc = nlp(text)
    assert len(doc) > 5

    nlp.add_pipe("emoji")
    doc = nlp(text)
    assert len(doc) == 5
    assert doc._.has_emoji
    assert doc[2]._.is_emoji
    assert len(doc[2].text) > 1


def test_custom_attrs():
    attrs = ("contains_emoji", "equals_emoji", "emoji_details", "all_emoji")
    nlp = English()
    nlp.add_pipe("emoji", config={"attrs": attrs})
    doc = nlp("Hello 🎉")
    assert doc._.all_emoji
    assert len(doc._.all_emoji) == 1
    assert doc[1]._.has("equals_emoji")
    assert doc[1]._.emoji_details


def test_lookup(nlp):
    nlp.add_pipe("emoji", config={"lookup": {"👨‍🎤": "David Bowie"}})
    doc = nlp("We can be 👨‍🎤 heroes")
    assert doc._.has_emoji
    assert doc[3]._.is_emoji
    assert doc[3]._.emoji_desc == "David Bowie"


@pytest.mark.parametrize("pattern_id", ["CUSTOM_ID"])
def test_pattern_id(nlp, pattern_id):
    emoji = Emoji(nlp, pattern_id=pattern_id)
    assert pattern_id in emoji.matcher
    assert "EMOJI" not in emoji.matcher


def test_usage_merge_overlapping(nlp):
    nlp.add_pipe("emoji")
    text = "🇺🇸🇦🇷"
    doc = nlp(text)
    assert len(doc) == 2
    assert doc[0].orth_ == text[0:2]
    assert doc[1].orth_ == text[2:4]


@pytest.mark.xfail
def test_final_variation_selector(nlp):
    """spaCy's tokenizer doesn't recognize the unicode variation selector as
    part of the emoji, which ends up being the first byte of the following
    token instead, if the emoji is not separated from the following text by
    a space.
    """
    # To work properly, text can be preprocessed by inserting a space between
    # the variation selector and any directly following ascii character, e.g.:
    # VARIATION_THEN_ASCII = re.compile(r"(\ufe0f)(\w)", flags=re.ASCII)
    # VARIATION_THEN_ASCII.sub(r"\1 \2", txt)
    nlp.add_pipe("emoji")
    txt = "🧟‍♀️This is a text with composed emojis 🧙‍♀️"
    doc = nlp(txt)

    # These are the 4 bytes representing the first emoji
    assert txt[:4].encode("raw_unicode_escape") == b"\\U0001f9df\\u200d\\u2640\\ufe0f"
    assert doc[0].orth_ == "🧟‍♀️"
    assert (
        doc[0].orth_.encode("raw_unicode_escape") == b"\\U0001f9df\\u200d\\u2640\\ufe0f"
    )
    assert doc[1].orth_[0] == "T"
