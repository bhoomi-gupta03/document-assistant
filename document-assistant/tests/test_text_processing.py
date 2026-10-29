import pytest

from app.text_processing import (
    count_words,
    decode_text,
    extract_keywords,
    split_sentences,
    stem,
    tokenize,
)


def test_decode_text_strips_bom_and_normalizes_newlines():
    assert decode_text(b"\xef\xbb\xbfhello\r\nworld\r\n") == "hello\nworld"


def test_decode_text_rejects_empty_and_whitespace():
    with pytest.raises(ValueError):
        decode_text(b"")
    with pytest.raises(ValueError):
        decode_text(b"  \n\t ")


def test_decode_text_rejects_invalid_utf8():
    with pytest.raises(ValueError):
        decode_text(b"\xff\xfe\xfa")


def test_decode_text_rejects_binary_nul_bytes():
    with pytest.raises(ValueError):
        decode_text(b"abc\x00def")


def test_tokenize_lowercases_and_keeps_contractions():
    assert tokenize("Don't STOP, believing!") == ["don't", "stop", "believing"]


def test_count_words():
    assert count_words("one two  three\nfour") == 4
    assert count_words("") == 0


def test_split_sentences_handles_punctuation_and_paragraphs():
    text = "Hello world. How are you?  Fine!\n\nNew paragraph\nsecond line"
    assert split_sentences(text) == [
        "Hello world.",
        "How are you?",
        "Fine!",
        "New paragraph second line",
    ]


def test_extract_keywords_removes_stop_words_and_duplicates():
    assert extract_keywords("What is the capital of France?") == ["capital", "france"]
    assert extract_keywords("python Python PYTHON") == ["python"]
    assert extract_keywords("what is this?") == []


def test_stem_removes_simple_plurals_only():
    assert stem("uses") == "use"
    assert stem("class") == "class"
    assert stem("is") == "is"
