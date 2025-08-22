from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_quiz_and_export_json_html():
    payload = {
        "name": "Sample Quiz",
        "description": "A generated quiz",
        "rules": {
            "numberOfQuestions": 3,
            "allowedTypes": ["MCQ_SINGLE", "TRUE_FALSE", "SHORT_ANSWER", "NUMERIC", "MCQ_MULTI"],
            "difficultyDistribution": {"low": 50, "medium": 30, "high": 20},
            "shuffle": True,
        },
    }
    r = client.post("/api/quizzes", json=payload)
    assert r.status_code == 200
    quiz = r.json()

    r2 = client.get(f"/api/quizzes/{quiz['id']}/export", params={"format": "json"})
    assert r2.status_code == 200

    r3 = client.get(f"/api/quizzes/{quiz['id']}/export", params={"format": "html"})
    assert r3.status_code == 200
    assert "<!doctype html>" in r3.text.lower()


def test_regenerate_quiz():
    payload = {
        "name": "Regenerate Quiz",
        "description": None,
        "rules": {
            "numberOfQuestions": 2,
            "allowedTypes": ["MCQ_SINGLE", "TRUE_FALSE"],
            "shuffle": False,
        },
    }
    r = client.post("/api/quizzes", json=payload)
    assert r.status_code == 200
    quiz = r.json()

    new_rules = {
        "numberOfQuestions": 4,
        "allowedTypes": ["MCQ_SINGLE", "TRUE_FALSE", "SHORT_ANSWER"],
        "shuffle": True,
    }
    r2 = client.post(f"/api/quizzes/{quiz['id']}/generate", json=new_rules)
    assert r2.status_code == 200