import React from "react";

const RISK_STYLES = {
  Low: { bg: "bg-emerald-50", border: "border-emerald-300", text: "text-emerald-700", bar: "bg-emerald-500" },
  Medium: { bg: "bg-amber-50", border: "border-amber-300", text: "text-amber-700", bar: "bg-amber-500" },
  High: { bg: "bg-red-50", border: "border-red-300", text: "text-red-700", bar: "bg-red-500" },
};

export default function RiskResult({ result }) {
  if (!result) return null;

  const { predicted_risk, risk_probabilities } = result;
  const style = RISK_STYLES[predicted_risk] || RISK_STYLES.Medium;

  return (
    <div className={`rounded-xl border ${style.border} ${style.bg} p-6 max-w-xl w-full`}>
      <h3 className="text-sm font-medium text-slate-500 mb-1">Predicted Risk Category</h3>
      <p className={`text-3xl font-bold ${style.text} mb-4`}>{predicted_risk}</p>

      <div className="space-y-2">
        {Object.entries(risk_probabilities)
          .sort((a, b) => b[1] - a[1])
          .map(([category, prob]) => (
            <div key={category}>
              <div className="flex justify-between text-xs text-slate-600 mb-0.5">
                <span>{category}</span>
                <span>{(prob * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                <div
                  className={`h-full ${RISK_STYLES[category]?.bar || "bg-slate-400"}`}
                  style={{ width: `${prob * 100}%` }}
                />
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
