import pytest

from molten import testing
from app import app

client = testing.TestClient(app)

def test_index_returns_200():
    resp = client.get(app.reverse_uri("health"))
    assert resp.status_code == 200
    assert resp.json()['version'] == '0.1'

def test_index_not_allowed_post():
    resp = client.post(app.reverse_uri("health"))
    assert resp.status_code == 404

def test_index_not_allowed_get():
    resp = client.get(app.reverse_uri("predict"))
    assert resp.status_code == 404
