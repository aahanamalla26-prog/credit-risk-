"""
Generates a synthetic credit risk dataset.

The dataset simulates loan applicants with realistic financial attributes.
Risk labels are derived from an underlying (noisy) probability-of-default
model, so classification is genuinely hard (not trivially separable) --
this mirrors real-world credit risk data.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

N = 12000  # 10,000+ records

def generate_dataset(n=N):
    age = np.random.randint(21, 65, size=n)
    annual_income = np.round(np.random.lognormal(mean=10.8, sigma=0.5, size=n), 2)  # skewed income
    employment_years = np.clip(np.random.exponential(scale=5, size=n), 0, 40).round(1)
    loan_amount = np.round(np.random.lognormal(mean=9.5, sigma=0.6, size=n), 2)
    credit_score = np.clip(np.random.normal(650, 80, size=n), 300, 850).round().astype(int)
    existing_debt = np.round(np.random.lognormal(mean=8.5, sigma=0.8, size=n), 2)
    num_open_accounts = np.random.randint(0, 15, size=n)
    previous_defaults = np.random.binomial(1, 0.12, size=n)
    loan_purpose = np.random.choice(
        ["debt_consolidation", "home_improvement", "business", "education", "medical", "other"],
        size=n, p=[0.30, 0.20, 0.15, 0.15, 0.10, 0.10]
    )

    debt_to_income = np.round(existing_debt / (annual_income + 1), 4)
    loan_to_income = np.round(loan_amount / (annual_income + 1), 4)

    # Underlying, noisy probability-of-default model.
    # Real relationships (lower credit score, higher DTI, prior defaults -> riskier)
    # plus substantial random noise, so it's not perfectly separable.
    z = (
        -0.010 * (credit_score - 650)
        + 3.2 * debt_to_income
        + 2.0 * loan_to_income
        + 1.6 * previous_defaults
        - 0.05 * employment_years
        - 0.004 * (annual_income / 1000)
        + 0.02 * num_open_accounts
        + np.random.normal(0, 1.3, size=n)  # noise dominates on purpose
    )
    default_prob = 1 / (1 + np.exp(-z))

    # Discretize into 3 risk tiers using probability terciles with added randomness
    risk_score = default_prob + np.random.normal(0, 0.08, size=n)
    low_cut, high_cut = np.quantile(risk_score, [0.45, 0.80])
    risk_category = np.where(risk_score <= low_cut, "Low",
                       np.where(risk_score <= high_cut, "Medium", "High"))

    df = pd.DataFrame({
        "age": age,
        "annual_income": annual_income,
        "employment_years": employment_years,
        "loan_amount": loan_amount,
        "credit_score": credit_score,
        "existing_debt": existing_debt,
        "num_open_accounts": num_open_accounts,
        "previous_defaults": previous_defaults,
        "loan_purpose": loan_purpose,
        "debt_to_income": debt_to_income,
        "loan_to_income": loan_to_income,
        "risk_category": risk_category,
    })
    return df

if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("/home/claude/credit-risk-platform/backend/data/applicants.csv", index=False)
    print(f"Generated {len(df)} records")
    print(df["risk_category"].value_counts())
    print(df.head())
