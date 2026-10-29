def upload(client, name="notes.txt", data=b"Python is great. FastAPI is fast.", ctype="text/plain"):
    return client.post("/documents", files={"file": (name, data, ctype)})


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# ---------- upload ----------
def test_upload_success_returns_metadata(client):
    r = upload(client)
    assert r.status_code == 201
    body = r.json()
    assert body["filename"] == "notes.txt"
    assert body["word_count"] == 6
    assert body["sentence_count"] == 2
    assert "content" not in body


def test_upload_rejects_wrong_extension(client):
    assert upload(client, name="malware.exe").status_code == 415
    assert upload(client, name="image.png", ctype="image/png").status_code == 415


def test_upload_rejects_empty_file(client):
    assert upload(client, data=b"   \n").status_code == 400


def test_upload_rejects_non_utf8_and_binary(client):
    assert upload(client, data=b"\xff\xfe\xfa").status_code == 400
    assert upload(client, data=b"abc\x00def").status_code == 400


def test_upload_rejects_too_large_file(client):
    assert upload(client, data=b"a" * 1_000_001).status_code == 413


def test_upload_requires_file_field(client):
    assert client.post("/documents").status_code == 422


def test_upload_strips_directory_parts_from_filename(client):
    r = upload(client, name="../../etc/passwd.txt")
    assert r.status_code == 201
    assert r.json()["filename"] == "passwd.txt"


# ---------- list / get / delete ----------
def test_list_with_pagination(client):
    for i in range(3):
        upload(client, name=f"{i}.txt")
    body = client.get("/documents", params={"limit": 2}).json()
    assert body["total"] == 3
    assert [d["filename"] for d in body["items"]] == ["2.txt", "1.txt"]
    body = client.get("/documents", params={"limit": 2, "offset": 2}).json()
    assert [d["filename"] for d in body["items"]] == ["0.txt"]


def test_list_validates_pagination(client):
    assert client.get("/documents", params={"limit": 0}).status_code == 422
    assert client.get("/documents", params={"limit": 101}).status_code == 422
    assert client.get("/documents", params={"offset": -1}).status_code == 422


def test_get_document_returns_content(client):
    doc_id = upload(client).json()["id"]
    r = client.get(f"/documents/{doc_id}")
    assert r.status_code == 200
    assert r.json()["content"] == "Python is great. FastAPI is fast."


def test_get_missing_and_invalid_id(client):
    assert client.get("/documents/999").status_code == 404
    assert client.get("/documents/abc").status_code == 422


def test_delete_document(client):
    doc_id = upload(client).json()["id"]
    assert client.delete(f"/documents/{doc_id}").status_code == 204
    assert client.get(f"/documents/{doc_id}").status_code == 404
    assert client.delete(f"/documents/{doc_id}").status_code == 404


# ---------- search ----------
def test_search_finds_matching_documents(client):
    upload(client, name="a.txt", data=b"Python and FastAPI are great.")
    upload(client, name="b.txt", data=b"Only Python here.")
    body = client.get("/documents/search", params={"q": "python"}).json()
    assert body["total"] == 2
    body = client.get("/documents/search", params={"q": "python fastapi"}).json()
    assert body["total"] == 1
    assert body["results"][0]["filename"] == "a.txt"
    assert "FastAPI" in body["results"][0]["snippet"] or "Python" in body["results"][0]["snippet"]


def test_search_no_results_and_validation(client):
    upload(client)
    assert client.get("/documents/search", params={"q": "zebra"}).json()["total"] == 0
    assert client.get("/documents/search", params={"q": "a"}).status_code == 422
    assert client.get("/documents/search").status_code == 422
    assert client.get("/documents/search", params={"q": "!!"}).status_code == 400


def test_search_route_is_not_shadowed_by_id_route(client):
    assert client.get("/documents/search", params={"q": "anything"}).status_code == 200


# ---------- ask ----------
def test_ask_returns_best_sentence_with_source(client):
    upload(client, name="p.txt", data=b"The project uses SQLite for storage. It is built with FastAPI.")
    r = client.post("/ask", json={"question": "What is it built with?"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "It is built with FastAPI."
    assert body["sources"][0]["filename"] == "p.txt"


def test_ask_can_be_limited_to_one_document(client):
    first = upload(client, name="a.txt", data=b"Cats are small animals.").json()["id"]
    upload(client, name="b.txt", data=b"Cats are independent pets.")
    r = client.post("/ask", json={"question": "What are cats?", "document_id": first})
    assert {s["document_id"] for s in r.json()["sources"]} == {first}


def test_ask_without_match_returns_null_answer(client):
    upload(client)
    body = client.post("/ask", json={"question": "Tell me about elephants"}).json()
    assert body["answer"] is None
    assert body["sources"] == []


def test_ask_validation_and_errors(client):
    assert client.post("/ask", json={"question": "hi"}).status_code == 422
    assert client.post("/ask", json={}).status_code == 422
    assert client.post("/ask", json={"question": "what is this?"}).status_code == 400
    assert client.post("/ask", json={"question": "What is Python?", "document_id": 99}).status_code == 404
