import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_get_question():
    payload = {
        "stem": "What is 2+2?",
        "type": "MCQ_SINGLE",
        "choices": ["3", "4"],
        "correctIndexes": [1],
        "acceptableAnswers": [],
        "numericAnswer": None,
        "explanation": "Basic addition",
        "difficulty": 1,
        "tags": ["math"],
        "subject": "Mathematics",
        "gradeLevel": "3",
        "bloomLevel": "Apply",
        "mediaImageUrl": None,
        "mediaAudioUrl": None,
    }
    r = client.post("/api/questions", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    qid = data["id"]
    assert data["stem"] == payload["stem"]
    assert data["type"] == payload["type"]

    r2 = client.get(f"/api/questions/{qid}")
    assert r2.status_code == 200
    got = r2.json()
    assert got["id"] == qid


def test_validation_mcq_bounds():
    payload = {
        "stem": "Bad mcq",
        "type": "MCQ_SINGLE",
        "choices": ["A"],
        "correctIndexes": [0],
        "acceptableAnswers": [],
        "difficulty": 2,
        "tags": [],
        "subject": "X",
        "gradeLevel": "Y",
        "bloomLevel": "Z",
    }
    r = client.post("/api/questions", json=payload)
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert any("at least 2 choices" in e for e in detail)


def test_search_and_pagination():
    r = client.get("/api/questions", params={"query": "capital", "page": 1, "size": 5})
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list)


def test_versioning_restore():
    # create question
    payload = {
        "stem": "Original stem",
        "type": "SHORT_ANSWER",
        "acceptableAnswers": ["foo"],
        "choices": [],
        "correctIndexes": [],
        "difficulty": 1,
        "tags": [],
        "subject": "Test",
        "gradeLevel": "G",
        "bloomLevel": "Remember",
    }
    r = client.post("/api/questions", json=payload)
    assert r.status_code == 201
    q = r.json()

    # update
    payload["stem"] = "Changed stem"
    r2 = client.put(f"/api/questions/{q['id']}", json=payload)
    assert r2.status_code == 200

    # list versions
    r3 = client.get(f"/api/questions/{q['id']}/versions")
    assert r3.status_code == 200
    versions = r3.json()
    assert len(versions) >= 1

    # restore first version
    ver = versions[0]["version"]
    r4 = client.post(f"/api/questions/{q['id']}/restore", params={"version": ver})
    assert r4.status_code == 200
    restored = r4.json()
    assert restored["stem"] == "Original stem"