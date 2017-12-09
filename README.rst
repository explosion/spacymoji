spacymoji: emoji for spaCy
**************************

`spaCy v2.0 <https://spacy.io/usage/v2>`_ extension and pipeline component
for adding emoji meta data to ``Doc`` objects. Detects emoji consisting of one
or more unicode characters, and can optionally merge multi-char emoji (combined
pictures, emoji with skin tone modifiers) into one token. Human-readable emoji
descriptions are added as a custom attribute, and an optional lookup table can
be provided for your own descriptions. The extension sets the custom ``Doc``,
``Token`` and ``Span`` attributes ``._.is_emoji``, ``._.emoji_desc``,
``._.has_emoji`` and ``._.emoji``. You can read more about custom pipeline
components and extension attributes
`here <https://spacy.io/usage/processing-pipelines>`_.

Emoji are matched using spaCy's ``PhraseMatcher``, and looked up in the data
table provided by the `"emoji" package <https://github.com/carpedm20/emoji>`_.

.. image:: https://img.shields.io/github/release/ines/spacymoji.svg?style=flat-square
    :target: https://github.com/ines/spacymoji/releases
    :alt: Current Release Version

.. image:: https://img.shields.io/pypi/v/spacymoji.svg?style=flat-square
    :target: https://pypi.python.org/pypi/spacymoji
    :alt: pypi Version

⏳ Installation
===============

``spacymoji`` requires ``spacy`` v2.0.0 or higher.

.. code:: bash

    pip install spacymoji

☝️ Usage
========

Import the component and initialise it with the shared ``nlp`` object (i.e. an
instance of ``Language``), which is used to initialise the ``PhraseMatcher``
with the shared vocab, and create the match patterns. Then add the component
anywhere in your pipeline.

.. code:: python

    import spacy
    from spacymoji import Emoji

    nlp = spacy.load('en')
    emoji = Emoji(nlp)
    nlp.add_pipe(emoji, first=True)

    doc = nlp(u"This is a test 😻 👍🏿")
    assert doc._.has_emoji == True
    assert doc[2:5]._.has_emoji == True
    assert doc[0]._.is_emoji == False
    assert doc[4]._.is_emoji == True
    assert doc[5]._.emoji_desc == u'thumbs up dark skin tone'
    assert len(doc._.emoji) == 2
    assert doc._.emoji[1] == (u'👍🏿', 5, u'thumbs up dark skin tone')

``spacymoji`` only cares about the token text, so you can use it on a blank
``Language`` instance (it should work for all
`available languages <https://spacy.io/usage/models#languages>`_!), or in
a pipeline with a loaded model. If you're loading a model and your pipeline
includes a tagger, parser and entity recognizer, make sure to add  the emoji
component as ``first=True``, so the spans are merged right after tokenization,
and *before* the document is parsed. If your text contains a lot of emoji, this
might even give you a nice boost in parser accuracy.

Available attributes
--------------------

The extension sets attributes on the ``Doc``, ``Span`` and ``Token``. You can
change the attribute names on initialisation of the extension. For more details
on custom components and attributes, see the
`processing pipelines documentation <https://spacy.io/usage/processing-pipelines#custom-components>`_.

====================== ======= ===
``Token._.is_emoji``   bool    Whether the token is an emoji.
``Token._.emoji_desc`` unicode A human-readable description of the emoji.
``Doc._.has_emoji``    bool    Whether the document contains emoji.
``Doc._.emoji``        list    ``(emoji, index, description)`` tuples of the document's emoji.
``Span._.has_emoji``   bool    Whether the span contains emoji.
``Span._.emoji``       list    ``(emoji, index, description)`` tuples of the span's emoji.
====================== ======= ===

Settings
--------

On initialisation of ``Emoji``, you can define the following settings:

=============== ============ ===
``nlp``         ``Language`` The shared ``nlp`` object. Used to initialise the matcher with the shared ``Vocab``, and create ``Doc`` match patterns.
``attrs``       tuple        Attributes to set on the ._ property. Defaults to ``('has_emoji', 'is_emoji', 'emoji_desc', 'emoji')``.
``pattern_id``  unicode      ID of match pattern, defaults to ``'EMOJI'``. Can be changed to avoid ID conflicts.
``merge_spans`` bool         Merge spans containing multi-character emoji, defaults to ``True``. Will only merge combined emoji resulting in one icon, not sequences.
``lookup``      dict         Optional lookup table that maps emoji unicode strings to custom descriptions, e.g. translations or other annotations.
=============== ============ ===

.. code:: python

    emoji = Emoji(nlp, attrs=('has_e', 'is_e', 'e_desc', 'e'), lookup={u'👨‍🎤': u'David Bowie'})
    nlp.add_pipe(emoji)
    doc = nlp(u"We can be 👨‍🎤 heroes")
    assert doc[3]._.is_e
    assert doc[3]._.e_desc == u'David Bowie'

🛣 Roadmap
==========

This extension is still experimental, but here are some features that might
be cool to add in the future:

* **Add match patterns and attributes for emoji shortcodes**, e.g. ``:+1:``. The shortcodes could optionally be merged into one token, and receive a ``NORM`` attribute with the unicode emoji. The ``NORM`` is used as a feature for training, so ``:+1:`` and 👍 would automatically receive similar representations.

* **Add support for the Unicode Emoji Annotations project**. The JavaScript `package <https://github.com/dematerializer/unicode-emoji-annotations>`_ also comes with `pre-compiled JSON data <https://github.com/dematerializer/unicode-emoji-annotations/tree/master/res>`_, including both standardised and community-contributed annotations in English and German.
