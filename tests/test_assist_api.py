from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_assist_diagnose_suggests_bloom_level():
    r = client.post("/api/assist/diagnose", json={"stem": "Describe the process of evaporation."})
    assert r.status_code == 200
    body = r.json()
    assert body["suggestedBloomLevel"] in ("Understand", None)
    assert isinstance(body["issues"], list)