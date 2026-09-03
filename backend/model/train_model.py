"""
Trains the credit risk model in two stages:

1. K-MEANS CLUSTERING: segments applicants into unsupervised risk groups based
   on their financial profile (income, debt ratios, credit score, etc). This
   cluster ID is added as an engineered feature -- it captures nonlinear
   groupings in the financial data that raw features alone don't expose.

2. RANDOM FOREST CLASSIFIER: trained on the original features PLUS the
   K-means cluster label to predict the final risk category (Low/Medium/High).
   Hyperparameters are tuned via grid search over a small param grid.

Outputs: model/risk_model.joblib (bundles the scaler, kmeans, encoder, and
trained RandomForest together), plus prints evaluation metrics.
"""
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "applicants.csv"
MODEL_PATH = Path(__file__).resolve().parent / "risk_model.joblib"
METRICS_PATH = Path(__file__).resolve().parent / "metrics.json"

NUMERIC_FEATURES = [
    "age", "annual_income", "employment_years", "loan_amount",
    "credit_score", "existing_debt", "num_open_accounts",
    "previous_defaults", "debt_to_income", "loan_to_income",
]
CATEGORICAL_FEATURES = ["loan_purpose"]
CLUSTER_INPUT_FEATURES = [
    "annual_income", "existing_debt", "credit_score",
    "debt_to_income", "loan_to_income",
]

def main():
    df = pd.read_csv(DATA_PATH)

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y = df["risk_category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # --- Stage 1: K-means clustering on financial features ---
    cluster_scaler = StandardScaler()
    X_train_cluster_input = cluster_scaler.fit_transform(X_train[CLUSTER_INPUT_FEATURES])
    X_test_cluster_input = cluster_scaler.transform(X_test[CLUSTER_INPUT_FEATURES])

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    kmeans.fit(X_train_cluster_input)

    X_train = X_train.copy()
    X_test = X_test.copy()
    X_train["risk_cluster"] = kmeans.predict(X_train_cluster_input).astype(str)
    X_test["risk_cluster"] = kmeans.predict(X_test_cluster_input).astype(str)

    all_categorical = CATEGORICAL_FEATURES + ["risk_cluster"]

    # --- Stage 2: preprocessing + Random Forest, tuned via grid search ---
    preprocessor = ColumnTransformer(transformers=[
        ("num", StandardScaler(), NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), all_categorical),
    ])

    pipeline = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("clf", RandomForestClassifier(random_state=42, class_weight="balanced")),
    ])

    param_grid = {
        "clf__n_estimators": [150, 300],
        "clf__max_depth": [8, 12, None],
        "clf__min_samples_leaf": [1, 3],
    }

    grid = GridSearchCV(pipeline, param_grid, cv=3, scoring="f1_macro", n_jobs=-1)
    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")

    print("Best params:", grid.best_params_)
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 (macro): {f1_macro:.4f}")
    print(classification_report(y_test, y_pred))

    # Bundle everything needed for inference
    bundle = {
        "model": best_model,
        "kmeans": kmeans,
        "cluster_scaler": cluster_scaler,
        "cluster_input_features": CLUSTER_INPUT_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
    }
    joblib.dump(bundle, MODEL_PATH)

    metrics = {
        "accuracy": round(accuracy, 4),
        "f1_macro": round(f1_macro, 4),
        "best_params": grid.best_params_,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nModel saved to {MODEL_PATH}")
    print(f"Metrics saved to {METRICS_PATH}")

if __name__ == "__main__":
    main()
