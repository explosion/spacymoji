# spacymoji: emoji for spaCy

[spaCy](https://spacy.io) extension and pipeline component
for adding emoji meta data to `Doc` objects. Detects emoji consisting of one
or more unicode characters, and can optionally merge multi-char emoji (combined
pictures, emoji with skin tone modifiers) into one token. Human-readable emoji
descriptions are added as a custom attribute, and an optional lookup table can
be provided for your own descriptions. The extension sets the custom `Doc`,
`Token` and `Span` attributes `._.is_emoji`, `._.emoji_desc`, `._.has_emoji` and `._.emoji`. You can read more about custom pipeline components and extension attributes [here](https://spacy.io/usage/processing-pipelines).

Emoji are matched using spaCy's [`PhraseMatcher`](https://spacy.io/api/phrasematcher), and looked up in the data
table provided by the [`emoji` package](https://github.com/carpedm20/emoji).

[![Azure Pipelines](https://img.shields.io/azure-devops/build/explosion-ai/public/22/master.svg?logo=azure-pipelines&style=flat-square&label=build)](https://dev.azure.com/explosion-ai/public/_build?definitionId=22)
[![Current Release Version](https://img.shields.io/github/release/explosion/spacymoji.svg?style=flat-square&logo=github)](https://github.com/explosion/spacymoji/releases)
[![pypi Version](https://img.shields.io/pypi/v/spacymoji.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/spacymoji/)

# ⏳ Installation

`spacymoji` requires `spacy` v3.0.0 or higher. For spaCy v2.x, instally `spacymoji==2.0.0`.

```bash
pip install spacymoji
```

# ☝️ Usage

Import the component and add it anywhere in your pipeline using the string
name of the `"emoji"` component factory:

```python
import spacy

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("emoji", first=True)
doc = nlp("This is a test 😻 👍🏿")
assert doc._.has_emoji is True
assert doc[2:5]._.has_emoji is True
assert doc[0]._.is_emoji is False
assert doc[4]._.is_emoji is True
assert doc[5]._.emoji_desc == "thumbs up dark skin tone"
assert len(doc._.emoji) == 2
assert doc._.emoji[1] == ("👍🏿", 5, "thumbs up dark skin tone")
```

`spacymoji` only cares about the token text, so you can use it on a blank
`Language` instance (it should work for all
[available languages](https://spacy.io/usage/models#languages)!), or in
a pipeline with a loaded pipeline. If your pipeline
includes a tagger, parser and entity recognizer, make sure to add the emoji
component as `first=True`, so the spans are merged right after tokenization,
and _before_ the document is parsed. If your text contains a lot of emoji, this
might even give you a nice boost in parser accuracy.

## Available attributes

The extension sets attributes on the `Doc`, `Span` and `Token`. You can
change the attribute names (and other parameters of the Emoji component) by passing
them via the `config` parameter in the `nlp.add_pipe(...)` method. For more details
on custom components and attributes, see the
[processing pipelines documentation](https://spacy.io/usage/processing-pipelines#custom-components).

| Attribute            | Type                       | Description                                                   |
| -------------------- | -------------------------- | ------------------------------------------------------------- |
| `Token._.is_emoji`   | bool                       | Whether the token is an emoji.                                |
| `Token._.emoji_desc` | str                        | A human-readable description of the emoji.                    |
| `Doc._.has_emoji`    | bool                       | Whether the document contains emoji.                          |
| `Doc._.emoji`        | List[Tuple[str, int, str]] | `(emoji, index, description)` tuples of the document's emoji. |
| `Span._.has_emoji`   | bool                       | Whether the span contains emoji.                              |
| `Span._.emoji`       | List[Tuple[str, int, str]] | `(emoji, index, description)` tuples of the span's emoji.     |

## Settings

You can configure the `emoji` factory by setting any of the following parameters in
the `config` dictionary:

| Setting       | Type                      | Description                                                                                                                            |
| ------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `attrs`       | Tuple[str, str, str, str] | Attributes to set on the `._` property. Defaults to `('has_emoji', 'is_emoji', 'emoji_desc', 'emoji')`.                                |
| `pattern_id`  | str                       | ID of match pattern, defaults to `'EMOJI'`. Can be changed to avoid ID conflicts.                                                      |
| `merge_spans` | bool                      | Merge spans containing multi-character emoji, defaults to `True`. Will only merge combined emoji resulting in one icon, not sequences. |
| `lookup`      | Dict[str, str]            | Optional lookup table that maps emoji strings to custom descriptions, e.g. translations or other annotations.                          |

```python
emoji_config = {"attrs": ("has_e", "is_e", "e_desc", "e"), lookup={"👨‍🎤": "David Bowie"})
nlp.add_pipe(emoji, first=True, config=emoji_config)
doc = nlp("We can be 👨‍🎤 heroes")
assert doc[3]._.is_e
assert doc[3]._.e_desc == "David Bowie"
```

If you're training a pipeline, you can define the component config in your [`config.cfg`](https://spacy.io/usage/training):

```ini
[nlp]
pipeline = ["emoji", "ner"]
# ...

[components.emoji]
factory = "emoji"
merge_spans = false
```
