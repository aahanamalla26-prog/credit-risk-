const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed with status ${res.status}`);
  }
  return data;
}

export async function submitApplicant(applicant) {
  const res = await fetch(`${API_BASE}/applicants`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(applicant),
  });
  return handleResponse(res);
}

export async function fetchApplicants(page = 1, perPage = 10) {
  const res = await fetch(`${API_BASE}/applicants?page=${page}&per_page=${perPage}`);
  return handleResponse(res);
}

export async function fetchApplicant(id) {
  const res = await fetch(`${API_BASE}/applicants/${id}`);
  return handleResponse(res);
}
