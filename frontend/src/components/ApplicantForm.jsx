import React, { useState } from "react";

const LOAN_PURPOSES = [
  "debt_consolidation",
  "home_improvement",
  "business",
  "education",
  "medical",
  "other",
];

const initialForm = {
  age: "",
  annual_income: "",
  employment_years: "",
  loan_amount: "",
  credit_score: "",
  existing_debt: "",
  num_open_accounts: "",
  previous_defaults: "0",
  loan_purpose: LOAN_PURPOSES[0],
};

export default function ApplicantForm({ onSubmit, submitting }) {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function validate() {
    const newErrors = {};
    const numericFields = [
      "age", "annual_income", "employment_years", "loan_amount",
      "credit_score", "existing_debt", "num_open_accounts",
    ];
    numericFields.forEach((field) => {
      if (form[field] === "" || isNaN(Number(form[field]))) {
        newErrors[field] = "Required, must be a number";
      }
    });
    if (Number(form.credit_score) < 300 || Number(form.credit_score) > 850) {
      newErrors.credit_score = "Credit score must be between 300 and 850";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;

    const payload = {
      age: Number(form.age),
      annual_income: Number(form.annual_income),
      employment_years: Number(form.employment_years),
      loan_amount: Number(form.loan_amount),
      credit_score: Number(form.credit_score),
      existing_debt: Number(form.existing_debt),
      num_open_accounts: Number(form.num_open_accounts),
      previous_defaults: Number(form.previous_defaults),
      loan_purpose: form.loan_purpose,
    };
    onSubmit(payload);
  }

  const fieldConfig = [
    { name: "age", label: "Age", type: "number" },
    { name: "annual_income", label: "Annual Income ($)", type: "number" },
    { name: "employment_years", label: "Employment (years)", type: "number", step: "0.1" },
    { name: "loan_amount", label: "Loan Amount ($)", type: "number" },
    { name: "credit_score", label: "Credit Score (300-850)", type: "number" },
    { name: "existing_debt", label: "Existing Debt ($)", type: "number" },
    { name: "num_open_accounts", label: "Open Accounts", type: "number" },
  ];

  return (
    <form onSubmit={handleSubmit} className="bg-white shadow rounded-xl p-6 space-y-4 max-w-xl w-full">
      <h2 className="text-xl font-semibold text-slate-800">Applicant Details</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {fieldConfig.map(({ name, label, type, step }) => (
          <div key={name}>
            <label className="block text-sm font-medium text-slate-600 mb-1">{label}</label>
            <input
              type={type}
              step={step}
              name={name}
              value={form[name]}
              onChange={handleChange}
              className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
                errors[name] ? "border-red-400" : "border-slate-300"
              }`}
            />
            {errors[name] && <p className="text-xs text-red-500 mt-1">{errors[name]}</p>}
          </div>
        ))}

        <div>
          <label className="block text-sm font-medium text-slate-600 mb-1">Loan Purpose</label>
          <select
            name="loan_purpose"
            value={form.loan_purpose}
            onChange={handleChange}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            {LOAN_PURPOSES.map((p) => (
              <option key={p} value={p}>{p.replace("_", " ")}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-600 mb-1">Previous Defaults</label>
          <select
            name="previous_defaults"
            value={form.previous_defaults}
            onChange={handleChange}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            <option value="0">No</option>
            <option value="1">Yes</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-lg py-2.5 transition-colors"
      >
        {submitting ? "Assessing..." : "Get Risk Assessment"}
      </button>
    </form>
  );
}
