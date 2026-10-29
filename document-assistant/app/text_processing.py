"""Pure text helpers: decoding, tokenizing, sentence splitting, keywords.
No web or database code here, so everything is easy to unit test."""
import re

_WORD_RE = re.compile(r"\w+(?:['’]\w+)?")
_PARAGRAPH_RE = re.compile(r"\n\s*\n")
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")

STOP_WORDS = frozenset(
    """a an the is are was were be been am do does did of in on at to for from by
    with about as into and or but if then than that this these those it its
    what which who whom whose when where why how i you he she we they me my your
    our their can could should would will shall may might has have had not no so
    there any some tell what's it's who's how's""".split()
)


def decode_text(raw: bytes) -> str:
    """Turn uploaded bytes into clean text, or raise ValueError with a
    message that is safe to show to the API user."""
    try:
        text = raw.decode("utf-8-sig")  # utf-8-sig also strips a BOM
    except UnicodeDecodeError as exc:
        raise ValueError("File is not valid UTF-8 text") from exc
    if "\x00" in text:
        raise ValueError("File looks like binary data, not plain text")
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        raise ValueError("File is empty")
    return text


def tokenize(text: str) -> list[str]:
    """Lowercase words: "Don't STOP" -> ["don't", "stop"]."""
    return _WORD_RE.findall(text.lower())


def count_words(text: str) -> int:
    return len(_WORD_RE.findall(text))


def split_sentences(text: str) -> list[str]:
    """Split on blank lines first, then on . ! ? followed by whitespace.
    Simple on purpose: abbreviations such as "Dr." will split wrongly."""
    sentences: list[str] = []
    for paragraph in _PARAGRAPH_RE.split(text):
        flat = " ".join(paragraph.split())  # collapse newlines/extra spaces
        sentences.extend(s for s in _SENTENCE_END_RE.split(flat) if s)
    return sentences


def extract_keywords(question: str) -> list[str]:
    """Unique, ordered, non-stop-word tokens of a question."""
    keywords: list[str] = []
    for token in tokenize(question):
        if token not in STOP_WORDS and token not in keywords:
            keywords.append(token)
    return keywords


def stem(word: str) -> str:
    """Tiny plural remover so "uses" matches "use". Not a real stemmer."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word
