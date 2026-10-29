"""Keyword search and extractive question answering.

Documents are plain dicts: {"id": int, "filename": str, "content": str}.
Nothing here touches the database or FastAPI."""
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from app.text_processing import extract_keywords, split_sentences, stem, tokenize


@dataclass(frozen=True)
class SearchHit:
    document_id: int
    filename: str
    score: int  # total occurrences of all query words
    snippet: str


@dataclass(frozen=True)
class Passage:
    document_id: int
    filename: str
    sentence: str
    score: float  # share of the question's keywords found in the sentence


def parse_query(query: str) -> list[str]:
    """Unique lowercase words of the query, order kept."""
    terms: list[str] = []
    for token in tokenize(query):
        if token not in terms:
            terms.append(token)
    return terms


def build_snippet(content: str, term: str, radius: int = 60) -> str:
    """A short piece of text around the first whole-word match of `term`."""
    match = re.search(rf"(?<!\w){re.escape(term)}(?!\w)", content, re.IGNORECASE)
    if match is None:
        return " ".join(content[: radius * 2].split())
    start = max(0, match.start() - radius)
    end = min(len(content), match.end() + radius)
    snippet = " ".join(content[start:end].split())
    return ("..." if start > 0 else "") + snippet + ("..." if end < len(content) else "")


def search_documents(documents: list[dict[str, Any]], query: str) -> list[SearchHit]:
    """Whole-word, case-insensitive search. Every query word must appear
    in a document (AND). Results are ranked by total occurrences."""
    terms = parse_query(query)
    if not terms:
        return []
    hits: list[SearchHit] = []
    for doc in documents:
        counts = Counter(tokenize(doc["content"]))
        if all(counts[t] > 0 for t in terms):
            hits.append(
                SearchHit(
                    document_id=doc["id"],
                    filename=doc["filename"],
                    score=sum(counts[t] for t in terms),
                    snippet=build_snippet(doc["content"], terms[0]),
                )
            )
    hits.sort(key=lambda h: (-h.score, h.document_id))
    return hits


def answer_question(
    documents: list[dict[str, Any]], question: str, top_k: int = 3
) -> list[Passage]:
    """Extractive Q&A: return the sentences that share the most keywords
    with the question. It copies existing sentences; it does NOT generate text."""
    keywords = {stem(k) for k in extract_keywords(question)}
    if not keywords:
        return []
    scored: list[tuple[float, int, int, Passage]] = []
    for doc in documents:
        for position, sentence in enumerate(split_sentences(doc["content"])):
            words = {stem(t) for t in tokenize(sentence)}
            overlap = len(keywords & words)
            if overlap == 0:
                continue
            score = round(overlap / len(keywords), 2)
            passage = Passage(doc["id"], doc["filename"], sentence, score)
            scored.append((-score, doc["id"], position, passage))
    scored.sort(key=lambda item: item[:3])  # best score, then doc order, then position
    return [item[3] for item in scored[:top_k]]
