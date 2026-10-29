from app.search import answer_question, build_snippet, search_documents

DOCS = [
    {"id": 1, "filename": "a.txt", "content": "Python is great. Python and FastAPI work well together."},
    {"id": 2, "filename": "b.txt", "content": "Only Java lives here."},
    {"id": 3, "filename": "c.txt", "content": "FastAPI is fast."},
]


def test_search_is_case_insensitive_and_ranks_by_occurrences():
    hits = search_documents(DOCS, "PYTHON")
    assert [h.document_id for h in hits] == [1]
    assert hits[0].score == 2


def test_search_requires_all_words():
    hits = search_documents(DOCS, "python fastapi")
    assert [h.document_id for h in hits] == [1]
    assert {h.document_id for h in search_documents(DOCS, "fastapi")} == {1, 3}


def test_search_matches_whole_words_only():
    docs = [{"id": 1, "filename": "x.txt", "content": "A pythonic style."}]
    assert search_documents(docs, "python") == []


def test_search_with_empty_or_symbol_query_returns_nothing():
    assert search_documents(DOCS, "") == []
    assert search_documents(DOCS, "!!!") == []


def test_snippet_contains_term_and_ellipses():
    text = "x " * 100 + "needle " + "y " * 100
    snippet = build_snippet(text, "needle")
    assert "needle" in snippet
    assert snippet.startswith("...") and snippet.endswith("...")


PROJECT = [
    {
        "id": 1,
        "filename": "project.txt",
        "content": "The project uses SQLite for storage. It is built with FastAPI. Tests are written with pytest.",
    }
]


def test_answer_finds_best_sentence():
    passages = answer_question(PROJECT, "What database does the project use?")
    assert passages[0].sentence == "The project uses SQLite for storage."
    assert passages[0].document_id == 1


def test_answer_perfect_keyword_match_scores_one():
    passages = answer_question(PROJECT, "What is it built with?")
    assert passages[0].sentence == "It is built with FastAPI."
    assert passages[0].score == 1.0


def test_answer_returns_nothing_when_no_overlap():
    assert answer_question(PROJECT, "Tell me about elephants") == []


def test_answer_respects_top_k():
    docs = [{"id": 1, "filename": "a.txt", "content": "Cats sleep. Cats eat. Cats play. Cats run."}]
    assert len(answer_question(docs, "what do cats do", top_k=2)) == 2
