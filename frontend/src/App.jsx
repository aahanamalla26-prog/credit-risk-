import React, { useState } from "react";
import ApplicantForm from "./components/ApplicantForm.jsx";
import RiskResult from "./components/RiskResult.jsx";
import ApplicantList from "./components/ApplicantList.jsx";
import { submitApplicant } from "./api";

export default function App() {
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  async function handleSubmit(payload) {
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const data = await submitApplicant(payload);
      setResult(data);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4">
      <div className="max-w-5xl mx-auto space-y-8">
        <header>
          <h1 className="text-2xl font-bold text-slate-800">Credit Risk Assessment Platform</h1>
          <p className="text-slate-500 text-sm mt-1">
            Submit applicant details to get a real-time, model-generated risk prediction.
          </p>
        </header>

        <div className="flex flex-col lg:flex-row gap-8 items-start">
          <ApplicantForm onSubmit={handleSubmit} submitting={submitting} />

          <div className="flex-1 space-y-4 w-full">
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3">
                {error}
              </div>
            )}
            {result ? (
              <RiskResult result={result} />
            ) : (
              <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-400 text-sm max-w-xl">
                Submit the form to see a risk prediction here.
              </div>
            )}
          </div>
        </div>

        <ApplicantList refreshKey={refreshKey} />
      </div>
    </div>
  );
}
