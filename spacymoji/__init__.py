from typing import Dict, Optional, Tuple, List, Union
from spacy.tokens import Doc, Span, Token
from spacy.matcher import PhraseMatcher
from spacy.language import Language
from spacy.util import filter_spans
from emoji import UNICODE_EMOJI


# Make sure multi-character emoji don't contain whitespace
EMOJI = {e.replace(" ", ""): t for e, t in UNICODE_EMOJI.items()}

DEFAULT_ATTRS = ("has_emoji", "is_emoji", "emoji_desc", "emoji")

DEFAULT_CONFIG = {
    "merge_spans": True,
    "lookup": {},
    "pattern_id": "EMOJI",
    "attrs": DEFAULT_ATTRS,
    "force_extension": True,
}


@Language.factory("emoji", default_config=DEFAULT_CONFIG)
def create_emoji(
    nlp: Language,
    name: str,
    merge_spans: bool = True,
    lookup: Optional[Dict[str, str]] = None,
    pattern_id: str = "EMOJI",
    attrs: Tuple[str, str, str, str] = DEFAULT_ATTRS,
    force_extension: bool = True,
):
    return Emoji(nlp, merge_spans, lookup, pattern_id, attrs, force_extension)


class Emoji:
    """spaCy v3.0 pipeline component for adding emoji meta data to `Doc` objects.
    Detects emoji consisting of one or more unicode characters, and can
    optionally merge multi-char emoji (combined pictures, emoji with skin tone
    modifiers) into one token. Emoji are matched using spaCy's `PhraseMatcher`,
    and looked up in the data table provided by the "emoji" package:
    https://github.com/carpedm20/emoji

    USAGE:
        >>> import spacy
        >>> from spacymoji import Emoji
        >>> nlp = spacy.load("en_core_web_sm")
        >>> nlp.add_pipe("emoji", first=True)
        >>> doc = nlp("This is a test 😻 👍🏿")
        >>> assert doc._.has_emoji is True
        >>> assert doc[2:5]._.has_emoji is True
        >>> assert doc[0]._.is_emoji is False
        >>> assert doc[4]._.is_emoji is True
        >>> assert doc[5]._.emoji_desc == "thumbs up dark skin tone"
        >>> assert len(doc._.emoji) == 2
        >>> assert doc._.emoji[1] == ("👍🏿", 5, "thumbs up dark skin tone")
    """

    name = "emoji"

    def __init__(
        self,
        nlp: Language,
        merge_spans: bool = True,
        lookup: Optional[Dict[str, str]] = None,
        pattern_id: str = "EMOJI",
        attrs: Tuple[str, str, str, str] = DEFAULT_ATTRS,
        force_extension: bool = True,
    ) -> None:
        """Initialise the pipeline component.

        nlp (Language): The shared nlp object. Used to initialise the matcher
            with the shared `Vocab`, and create `Doc` match patterns.
        attrs (tuple): Attributes to set on the ._ property. Defaults to
            ('has_emoji', 'is_emoji', 'emoji_desc', 'emoji').
        pattern_id (unicode): ID of match pattern, defaults to 'EMOJI'. Can be
            changed to avoid ID clashes.
        merge_spans (bool): Merge spans containing multi-character emoji. Will
            only merge combined emoji resulting in one icon, not sequences.
        lookup (dict): Optional lookup table that maps emoji unicode strings
            to custom descriptions, e.g. translations or other annotations.
        RETURNS (callable): A spaCy pipeline component.
        """
        self._has_emoji, self._is_emoji, self._emoji_desc, self._emoji = attrs
        self.merge_spans = merge_spans
        self.lookup = lookup or {}
        self.matcher = PhraseMatcher(nlp.vocab)
        emoji_patterns = list(nlp.tokenizer.pipe(EMOJI.keys()))
        self.matcher.add(pattern_id, None, *emoji_patterns)
        # Add attributes
        Doc.set_extension(self._has_emoji, getter=self.has_emoji, force=force_extension)
        Doc.set_extension(self._emoji, getter=self.iter_emoji, force=force_extension)
        Span.set_extension(
            self._has_emoji, getter=self.has_emoji, force=force_extension
        )
        Span.set_extension(self._emoji, getter=self.iter_emoji, force=force_extension)
        Token.set_extension(self._is_emoji, default=False, force=force_extension)
        Token.set_extension(
            self._emoji_desc, getter=self.get_emoji_desc, force=force_extension
        )

    def __call__(self, doc: Doc) -> Doc:
        """Apply the pipeline component to a `Doc` object.

        doc (Doc): The `Doc` returned by the previous pipeline component.
        RETURNS (Doc): The modified `Doc` object.
        """
        spans = self.matcher(doc, as_spans=True)
        for span in spans:
            for token in span:
                token._.set(self._is_emoji, True)

        if self.merge_spans:
            spans = filter_spans(spans)
            with doc.retokenize() as retokenizer:
                for span in spans:
                    if len(span) > 1:
                        retokenizer.merge(span)
        return doc

    def has_emoji(self, tokens: Union[Doc, Span]) -> bool:
        return any(token._.get(self._is_emoji) for token in tokens)

    def iter_emoji(self, tokens: Union[Doc, Span]) -> List[Tuple[str, int, str]]:
        return [
            (t.text, i, t._.get(self._emoji_desc))
            for i, t in enumerate(tokens)
            if t._.get(self._is_emoji)
        ]

    def get_emoji_desc(self, token: Token) -> Optional[str]:
        if token.text in self.lookup:
            return self.lookup[token.text]
        if token.text in EMOJI:
            desc = EMOJI[token.text]
            # Here we're converting shortcodes, e.g. ":man_getting_haircut:"
            return desc.replace("_", " ").replace(":", "")
        return None
