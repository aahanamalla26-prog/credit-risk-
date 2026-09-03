# AI-Powered Credit Risk Assessment Platform

A fullstack application that predicts credit risk (Low / Medium / High) for
loan applicants, using a K-means + Random Forest pipeline served through a
Flask REST API and a React frontend.

## How it works

1. **Data**: a synthetic dataset of 12,000 loan applicants is generated with
   realistic financial attributes (income, credit score, debt, loan amount,
   employment history, etc.), with risk labels derived from a noisy
   probability-of-default model — not perfectly separable, similar to
   real-world credit data.
2. **K-means clustering**: applicants are first clustered (unsupervised, 4
   clusters) on their financial profile (income, debt ratios, credit score).
   The cluster assignment is added as an engineered feature.
3. **Random Forest classifier**: trained on the original features plus the
   cluster feature, tuned via grid search (`n_estimators`, `max_depth`,
   `min_samples_leaf`), to predict the final risk category.
4. **Flask API**: exposes endpoints to submit an applicant (returns a live
   prediction) and to list/query past submissions, backed by a database.
5. **React + Tailwind frontend**: a form to submit applicant data, a visual
   breakdown of the predicted risk probabilities, and a submission history
   table.

## Model performance

On a held-out 20% test set (2,400 of 12,000 records):

| Metric | Value |
|---|---|
| Accuracy | 57.6% |
| F1 (macro) | 0.544 |

These numbers reflect a 3-class problem (Low/Medium/High) on data with
deliberately realistic noise — a random baseline on 3 imbalanced classes
would be well below 50%, so this is a genuine, non-trivial signal, not a
memorized or leaky result. Full classification report and best
hyperparameters are in `backend/model/metrics.json`.

## Project structure

```
credit-risk-platform/
├── backend/
│   ├── app.py                # Flask REST API
│   ├── schema.sql            # Production MySQL schema
│   ├── requirements.txt
│   ├── data/
│   │   └── generate_data.py  # Synthetic dataset generator
│   └── model/
│       └── train_model.py    # K-means + Random Forest training pipeline
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   └── components/
    │       ├── ApplicantForm.jsx
    │       ├── RiskResult.jsx
    │       └── ApplicantList.jsx
    └── package.json
```

## Running it locally

### Backend
```bash
cd backend
pip install -r requirements.txt
python data/generate_data.py     # generates data/applicants.csv
python model/train_model.py      # trains model/risk_model.joblib
python app.py                    # starts API on http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                      # starts dev server on http://localhost:5173
```

## Note on the database

The local/dev backend uses **SQLite** (zero setup, ships with Python) for
simplicity. `schema.sql` contains the equivalent **MySQL** schema for
production use — swapping `app.py`'s `sqlite3` calls for a MySQL connector
(e.g. `PyMySQL`) is a small, mechanical change since the table shape and
queries are unchanged.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/applicants` | Submit an applicant, get a risk prediction |
| GET | `/api/applicants` | List submitted applicants (paginated) |
| GET | `/api/applicants/<id>` | Get a single applicant + prediction |
| GET | `/api/health` | Health check |
