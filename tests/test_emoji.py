# coding: utf-8
from __future__ import unicode_literals

from spacy.lang.en import English
import pytest

from spacymoji import Emoji


@pytest.fixture(scope='function')
def nlp():
    return English()


def test_integration(nlp):
    emoji = Emoji(nlp)
    nlp.add_pipe(emoji, last=True)
    assert nlp.pipe_names[-1] == 'emoji'


@pytest.mark.parametrize('icon', [u'🐼', u'😇', u'\U0001F45E'])
def test_usage_single_emoji(nlp, icon):
    emoji = Emoji(nlp)
    nlp.add_pipe(emoji, last=True)
    doc = nlp(u"Hello %s world" % icon)
    assert doc._.has_emoji
    assert doc[1]._.is_emoji
    assert doc[1]._.emoji_desc == emoji.get_emoji_desc(doc[1])
    assert doc[1:3]._.has_emoji
    assert len(doc._.emoji) == 1
    emoji_text, emoji_idx, emoji_desc = doc._.emoji[0]
    assert emoji_text == icon
    assert emoji_idx == 1


def test_usage_no_emoji(nlp):
    emoji = Emoji(nlp)
    nlp.add_pipe(emoji, last=True)
    doc = nlp(u"In total there are 2,666 emojis in the Unicode Standard.")
    assert not doc._.has_emoji
    for token in doc:
        assert not token._.is_emoji


def test_usage_multiple_emoji(nlp):
    emoji = Emoji(nlp)
    nlp.add_pipe(emoji, last=True)
    doc = nlp(u"Hello 😻🍕 world, this ✨ 💥 is an example.")
    assert doc._.has_emoji
    assert len(doc._.emoji) == 4
    assert doc[:5]._.has_emoji
    assert len(doc[:5]._.emoji) == 2


@pytest.mark.parametrize('emoji', [u'👌🏾', u'👩‍💻', u'\U0001F933\U0001F3FD'])
def test_usage_merge_spans(nlp, emoji):
    text = u"This is %s a test" % emoji
    emoji = Emoji(nlp)
    doc = nlp(text)
    assert len(doc) > 5
    nlp.add_pipe(emoji, last=True)
    doc = nlp(text)
    assert len(doc) == 5
    assert doc._.has_emoji
    assert doc[2]._.is_emoji
    assert len(doc[2].text) > 1


def test_usage_merge_overlapping(nlp):
    text = '🇺🇸🇦🇷'
    assert len(text) == 4

    emoji = Emoji(nlp)
    nlp.add_pipe(emoji, last=True)
    doc = nlp(text)

    assert len(doc) == 2
    assert doc[0].orth_ == text[0:2]
    assert doc[1].orth_ == text[2:4]


def test_custom_attrs():
    attrs = ('contains_emoji', 'equals_emoji', 'emoji_details', 'all_emoji')
    nlp = English()
    emoji = Emoji(nlp, attrs=attrs)
    nlp.add_pipe(emoji, last=True)
    doc = nlp(u"Hello 🎉")
    assert doc._.all_emoji
    assert len(doc._.all_emoji) == 1
    assert doc[1]._.has('equals_emoji')
    assert doc[1]._.emoji_details



def test_lookup(nlp):
    emoji = Emoji(nlp, lookup={'👨‍🎤': 'David Bowie'})
    nlp.add_pipe(emoji, last=True)
    doc = nlp(u"We can be 👨‍🎤 heroes")
    assert doc._.has_emoji
    assert doc[3]._.is_emoji
    assert doc[3]._.emoji_desc == 'David Bowie'


@pytest.mark.parametrize('pattern_id', ['CUSTOM_ID'])
def test_pattern_id(nlp, pattern_id):
    emoji = Emoji(nlp, pattern_id=pattern_id)
    assert pattern_id in emoji.matcher
    assert not 'EMOJI' in emoji.matcher
