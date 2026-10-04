"""
Credit Risk Assessment Platform -- Flask REST API.

Endpoints:
  POST /api/applicants        Submit a new applicant, get a risk prediction
  GET  /api/applicants        List all submitted applicants (paginated)
  GET  /api/applicants/<id>   Get a single applicant + prediction by id
  GET  /api/health            Health check
"""
import sqlite3
import joblib
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify, g

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "credit_risk.db"
MODEL_PATH = APP_DIR / "model" / "risk_model.joblib"

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

_bundle = None
def get_model_bundle():
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            annual_income REAL NOT NULL,
            employment_years REAL NOT NULL,
            loan_amount REAL NOT NULL,
            credit_score INTEGER NOT NULL,
            existing_debt REAL NOT NULL,
            num_open_accounts INTEGER NOT NULL,
            previous_defaults INTEGER NOT NULL,
            loan_purpose TEXT NOT NULL,
            predicted_risk TEXT NOT NULL,
            risk_probabilities TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'submitted',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


REQUIRED_FIELDS = [
    "age", "annual_income", "employment_years", "loan_amount",
    "credit_score", "existing_debt", "num_open_accounts",
    "previous_defaults", "loan_purpose",
]


NUMERIC_RANGES = {
    "age": (18, 100),
    "annual_income": (0, 1e9),
    "employment_years": (0, 60),
    "loan_amount": (0, 1e9),
    "credit_score": (300, 850),
    "existing_debt": (0, 1e9),
    "num_open_accounts": (0, 100),
    "previous_defaults": (0, 100),
}


def validate_payload(payload):
    """Return an error message string, or None if the payload is valid."""
    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    for field, (low, high) in NUMERIC_RANGES.items():
        try:
            value = float(payload[field])
        except (TypeError, ValueError):
            return "One or more numeric fields are invalid"
        if not low <= value <= high:
            return f"{field} must be between {low} and {high}"
    if not isinstance(payload["loan_purpose"], str) or not payload["loan_purpose"].strip():
        return "loan_purpose must be a non-empty string"
    return None


def normalize_payload(payload):
    """Cast numeric fields to real numbers (the API may receive numeric strings)."""
    clean = dict(payload)
    for field in NUMERIC_RANGES:
        clean[field] = float(payload[field])
    return clean


def predict_risk(payload):
    bundle = get_model_bundle()
    row = {f: payload[f] for f in REQUIRED_FIELDS}
    row["debt_to_income"] = row["existing_debt"] / (row["annual_income"] + 1)
    row["loan_to_income"] = row["loan_amount"] / (row["annual_income"] + 1)

    df = pd.DataFrame([row])

    cluster_input = bundle["cluster_scaler"].transform(df[bundle["cluster_input_features"]])
    df["risk_cluster"] = bundle["kmeans"].predict(cluster_input).astype(str)

    model = bundle["model"]
    pred = model.predict(df)[0]
    proba = model.predict_proba(df)[0]
    classes = model.classes_
    proba_dict = {cls: round(float(p), 4) for cls, p in zip(classes, proba)}
    return pred, proba_dict


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/applicants", methods=["POST"])
def create_applicant():
    payload = request.get_json(silent=True) or {}
    error = validate_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    payload = normalize_payload(payload)
    try:
        predicted_risk, proba = predict_risk(payload)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

    db = get_db()
    cur = db.execute(
        """INSERT INTO applicants
           (age, annual_income, employment_years, loan_amount, credit_score,
            existing_debt, num_open_accounts, previous_defaults, loan_purpose,
            predicted_risk, risk_probabilities, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            payload["age"], payload["annual_income"], payload["employment_years"],
            payload["loan_amount"], payload["credit_score"], payload["existing_debt"],
            payload["num_open_accounts"], payload["previous_defaults"], payload["loan_purpose"],
            predicted_risk, str(proba), "submitted",
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    db.commit()

    return jsonify({
        "id": cur.lastrowid,
        "predicted_risk": predicted_risk,
        "risk_probabilities": proba,
    }), 201


@app.route("/api/applicants", methods=["GET"])
def list_applicants():
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
    except ValueError:
        return jsonify({"error": "page and per_page must be integers"}), 400
    offset = (page - 1) * per_page

    db = get_db()
    rows = db.execute(
        "SELECT * FROM applicants ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()
    total = db.execute("SELECT COUNT(*) as c FROM applicants").fetchone()["c"]

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "applicants": [dict(r) for r in rows],
    })


@app.route("/api/applicants/<int:applicant_id>", methods=["GET"])
def get_applicant(applicant_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM applicants WHERE id = ?", (applicant_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "Applicant not found"}), 404
    return jsonify(dict(row))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
