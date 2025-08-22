from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_export_json():
    r = client.get("/api/questions/export", params={"format": "json"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")


def test_export_csv():
    r = client.get("/api/questions/export", params={"format": "csv"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain") or r.headers["content-type"].startswith("text/csv")


def test_import_json_and_error_reporting():
    data = [
        {
            "stem": "X",
            "type": "SHORT_ANSWER",
            "acceptableAnswers": ["x"],
            "difficulty": 1,
            "tags": [],
            "subject": "S",
            "gradeLevel": "G",
            "bloomLevel": "Remember",
        },
        {
            "stem": "bad",
            "type": "MCQ_SINGLE",
            "choices": ["only one"],
            "correctIndexes": [0],
            "difficulty": 2,
            "tags": [],
            "subject": "S",
            "gradeLevel": "G",
            "bloomLevel": "Remember",
        },
    ]
    import json

    files = {"file": ("data.json", json.dumps(data), "application/json")}
    r = client.post("/api/questions/import", params={"format": "json"}, files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["created"] >= 1
    assert body["failed"] >= 1
    assert len(body["errors"]) >= 1