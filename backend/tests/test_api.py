"""Tests for the Credit Risk API: payload validation and /api/applicants routes.

Run from the backend/ folder:  python -m pytest -v
Each test uses a throwaway SQLite database, so real data is never touched.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import app as app_module  # noqa: E402


VALID_PAYLOAD = {
    "age": 35,
    "annual_income": 85000,
    "employment_years": 8,
    "loan_amount": 20000,
    "credit_score": 720,
    "existing_debt": 12000,
    "num_open_accounts": 4,
    "previous_defaults": 0,
    "loan_purpose": "home_improvement",
}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DB_PATH", tmp_path / "test.db")
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


# ---------- validate_payload (pure function) ----------

def test_validate_payload_accepts_valid_input():
    assert app_module.validate_payload(VALID_PAYLOAD) is None


def test_validate_payload_reports_missing_fields():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k not in ("age", "credit_score")}
    error = app_module.validate_payload(payload)
    assert "Missing required fields" in error
    assert "age" in error and "credit_score" in error


@pytest.mark.parametrize("field,value", [
    ("annual_income", -5), ("credit_score", 9999), ("credit_score", 100),
    ("age", 5), ("employment_years", -1),
])
def test_validate_payload_rejects_out_of_range_values(field, value):
    error = app_module.validate_payload({**VALID_PAYLOAD, field: value})
    assert error is not None and field in error


def test_validate_payload_rejects_blank_loan_purpose():
    assert "loan_purpose" in app_module.validate_payload({**VALID_PAYLOAD, "loan_purpose": "  "})


@pytest.mark.parametrize("bad_value", ["abc", None, [1, 2]])
def test_validate_payload_rejects_non_numeric_values(bad_value):
    payload = {**VALID_PAYLOAD, "annual_income": bad_value}
    assert app_module.validate_payload(payload) == "One or more numeric fields are invalid"


# ---------- /api/health ----------

def test_health_returns_ok(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


# ---------- POST /api/applicants ----------

def test_create_applicant_returns_prediction_and_201(client):
    res = client.post("/api/applicants", json=VALID_PAYLOAD)
    assert res.status_code == 201
    body = res.get_json()
    assert body["id"] == 1
    assert body["predicted_risk"] in {"Low", "Medium", "High"}
    probs = body["risk_probabilities"]
    assert set(probs) == {"Low", "Medium", "High"}
    assert sum(probs.values()) == pytest.approx(1.0, abs=0.01)


def test_create_applicant_missing_field_returns_400(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "loan_purpose"}
    res = client.post("/api/applicants", json=payload)
    assert res.status_code == 400
    assert "loan_purpose" in res.get_json()["error"]


def test_create_applicant_empty_body_returns_400(client):
    res = client.post("/api/applicants", data="not json", content_type="text/plain")
    assert res.status_code == 400


# ---------- GET /api/applicants and /api/applicants/<id> ----------

def test_list_applicants_empty_then_paginated(client):
    empty = client.get("/api/applicants").get_json()
    assert empty["total"] == 0 and empty["applicants"] == []

    for _ in range(3):
        client.post("/api/applicants", json=VALID_PAYLOAD)

    page = client.get("/api/applicants?per_page=2&page=1").get_json()
    assert page["total"] == 3
    assert len(page["applicants"]) == 2
    assert page["applicants"][0]["id"] == 3          # newest first

    page2 = client.get("/api/applicants?per_page=2&page=2").get_json()
    assert len(page2["applicants"]) == 1


def test_list_applicants_caps_per_page_at_100(client):
    assert client.get("/api/applicants?per_page=5000").get_json()["per_page"] == 100


def test_get_applicant_by_id_and_404(client):
    created = client.post("/api/applicants", json=VALID_PAYLOAD).get_json()
    found = client.get(f"/api/applicants/{created['id']}")
    assert found.status_code == 200
    assert found.get_json()["predicted_risk"] == created["predicted_risk"]

    missing = client.get("/api/applicants/9999")
    assert missing.status_code == 404
    assert missing.get_json()["error"] == "Applicant not found"


# ---------- regression tests for bugs found while testing ----------

def test_numeric_strings_are_accepted_not_500(client):
    res = client.post("/api/applicants", json={**VALID_PAYLOAD, "annual_income": "85000"})
    assert res.status_code == 201


def test_out_of_range_value_returns_400(client):
    res = client.post("/api/applicants", json={**VALID_PAYLOAD, "credit_score": 9999})
    assert res.status_code == 400


def test_invalid_pagination_returns_400_not_500(client):
    assert client.get("/api/applicants?page=abc").status_code == 400
