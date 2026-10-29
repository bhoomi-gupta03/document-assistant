from app import repository


def make(conn, name="a.txt", content="hello world"):
    return repository.create_document(
        conn, filename=name, size_bytes=len(content), content=content,
        word_count=len(content.split()), sentence_count=1,
    )


def test_create_and_get(conn):
    created = make(conn)
    assert created["id"] == 1
    assert created["uploaded_at"]
    assert repository.get_document(conn, 1)["content"] == "hello world"


def test_get_missing_returns_none(conn):
    assert repository.get_document(conn, 999) is None


def test_list_is_newest_first_without_content_and_paginates(conn):
    for i in range(3):
        make(conn, name=f"{i}.txt")
    items = repository.list_documents(conn, limit=2, offset=0)
    assert [d["filename"] for d in items] == ["2.txt", "1.txt"]
    assert "content" not in items[0]
    assert [d["filename"] for d in repository.list_documents(conn, 2, 2)] == ["0.txt"]
    assert repository.count_documents(conn) == 3


def test_delete(conn):
    make(conn)
    assert repository.delete_document(conn, 1) is True
    assert repository.delete_document(conn, 1) is False
    assert repository.count_documents(conn) == 0


def test_sql_injection_text_is_stored_as_plain_data(conn):
    make(conn, name="x.txt'); DROP TABLE documents;--")
    assert repository.count_documents(conn) == 1
