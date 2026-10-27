import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app  # noqa: E402

VALID = {
    "name": "Samreen",
    "reg_no": "FA23-BSE-015",
    "title": "Lab Assignment 1",
    "url": "https://github.com/example/repo",
}


@pytest.fixture
def setup(tmp_path):
    data_file = tmp_path / "submissions.json"
    client = create_app(str(data_file)).test_client()
    return client, data_file


def saved(data_file):
    if not data_file.exists():
        return []
    return json.loads(data_file.read_text())


def test_valid_submission_is_saved_and_listed(setup):
    client, data_file = setup
    resp = client.post("/", data=VALID)
    assert resp.status_code == 200
    assert len(saved(data_file)) == 1
    assert "Lab Assignment 1" in resp.get_data(as_text=True)


def test_missing_registration_number_is_rejected(setup):
    client, data_file = setup
    data = dict(VALID, reg_no="")
    resp = client.post("/", data=data)
    assert resp.status_code == 400
    assert "Registration number is required" in resp.get_data(as_text=True)
    assert saved(data_file) == []


def test_invalid_url_is_rejected_and_not_saved(setup):
    client, data_file = setup
    data = dict(VALID, url="not-a-url")
    resp = client.post("/", data=data)
    assert resp.status_code == 400
    assert "invalid" in resp.get_data(as_text=True).lower()
    assert saved(data_file) == []