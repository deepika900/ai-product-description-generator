import json
from types import SimpleNamespace

import pytest

from app import clean_list, create_app


def fake_client(payload):
    message = SimpleNamespace(content=json.dumps(payload))
    response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
    completions = SimpleNamespace(create=lambda **kwargs: response)
    return SimpleNamespace(chat=SimpleNamespace(completions=completions))


@pytest.fixture
def client():
    good = {"title": "Cotton Shirt", "description": "A soft shirt.", "bullets": ["Soft", "Breathable", "Easy care"]}
    return create_app(fake_client(good)).test_client()


def test_health(client):
    assert client.get("/api/health").status_code == 200


def test_name_is_required(client):
    res = client.post("/api/generate", json={"category": "Shirts"})
    assert res.status_code == 400


def test_rejects_unknown_tone(client):
    res = client.post("/api/generate", json={"name": "Shirt", "tone": "angry"})
    assert res.status_code == 400


def test_generate_success(client):
    res = client.post("/api/generate", json={"name": "Cotton Shirt", "features": "breathable, slim fit"})
    body = res.get_json()
    assert res.status_code == 200
    assert body["title"] == "Cotton Shirt"
    assert len(body["bullets"]) == 3
    assert "elapsed_ms" in body


def test_bad_model_output_returns_502():
    app = create_app(fake_client({"unexpected": True}))
    res = app.test_client().post("/api/generate", json={"name": "Shirt"})
    assert res.status_code == 502


def test_clean_list_handles_strings_and_lists():
    assert clean_list("a, b\nc") == ["a", "b", "c"]
    assert clean_list([" x ", "", "y"]) == ["x", "y"]
    assert clean_list(None) == []
