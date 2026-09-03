import React, { useEffect, useState, useCallback } from "react";
import { fetchApplicants } from "../api";

const BADGE_STYLES = {
  Low: "bg-emerald-100 text-emerald-700",
  Medium: "bg-amber-100 text-amber-700",
  High: "bg-red-100 text-red-700",
};

export default function ApplicantList({ refreshKey }) {
  const [applicants, setApplicants] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const perPage = 8;

  const load = useCallback(async (p) => {
    setLoading(true);
    try {
      const data = await fetchApplicants(p, perPage);
      setApplicants(data.applicants);
      setTotal(data.total);
      setPage(data.page);
    } catch (err) {
      console.error("Failed to load applicants:", err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(1);
  }, [refreshKey, load]);

  const totalPages = Math.max(Math.ceil(total / perPage), 1);

  return (
    <div className="bg-white shadow rounded-xl p-6 max-w-3xl w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-slate-800">Submission History</h2>
        <span className="text-sm text-slate-500">{total} total</span>
      </div>

      {loading ? (
        <p className="text-sm text-slate-500">Loading...</p>
      ) : applicants.length === 0 ? (
        <p className="text-sm text-slate-500">No applicants submitted yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="text-slate-500 border-b">
                <th className="py-2 pr-4">ID</th>
                <th className="py-2 pr-4">Income</th>
                <th className="py-2 pr-4">Loan</th>
                <th className="py-2 pr-4">Credit Score</th>
                <th className="py-2 pr-4">Purpose</th>
                <th className="py-2 pr-4">Risk</th>
                <th className="py-2 pr-4">Submitted</th>
              </tr>
            </thead>
            <tbody>
              {applicants.map((a) => (
                <tr key={a.id} className="border-b last:border-0">
                  <td className="py-2 pr-4">{a.id}</td>
                  <td className="py-2 pr-4">${Number(a.annual_income).toLocaleString()}</td>
                  <td className="py-2 pr-4">${Number(a.loan_amount).toLocaleString()}</td>
                  <td className="py-2 pr-4">{a.credit_score}</td>
                  <td className="py-2 pr-4">{a.loan_purpose.replace("_", " ")}</td>
                  <td className="py-2 pr-4">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${BADGE_STYLES[a.predicted_risk]}`}>
                      {a.predicted_risk}
                    </span>
                  </td>
                  <td className="py-2 pr-4 text-slate-500">
                    {new Date(a.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-between items-center mt-4">
          <button
            onClick={() => load(page - 1)}
            disabled={page <= 1}
            className="text-sm text-indigo-600 disabled:text-slate-300"
          >
            Previous
          </button>
          <span className="text-sm text-slate-500">Page {page} of {totalPages}</span>
          <button
            onClick={() => load(page + 1)}
            disabled={page >= totalPages}
            className="text-sm text-indigo-600 disabled:text-slate-300"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
