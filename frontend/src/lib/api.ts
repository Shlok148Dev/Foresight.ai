/**
 * Foresight — API Client
 * ========================
 * Axios instance with JWT interceptors and auto-refresh.
 */

import axios from "axios";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 15_000,
  headers: { "Content-Type": "application/json" },
});

/* ── Request interceptor: attach JWT ─────────────────────────── */

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("foresight_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

/* ── Response interceptor: handle 401 ────────────────────────── */

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("foresight_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

/* ── Typed API helpers ───────────────────────────────────────── */

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),

  register: (email: string, password: string, username: string, full_name?: string) =>
    api.post("/auth/register", { email, password, username, full_name }),

  me: () => api.get("/auth/me"),

  refresh: (refreshToken: string) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),
};

export const signalsApi = {
  list: (params?: { limit?: number; offset?: number; platform?: string }) =>
    api.get("/signals/", { params }),

  get: (id: string) => api.get(`/signals/${id}`),

  ingest: (data: { text: string; platform: string; author?: string; metadata?: Record<string, unknown> }) =>
    api.post("/signals/ingest", data),

  ingestBatch: (signals: Array<{ text: string; platform: string }>) =>
    api.post("/signals/ingest/batch", { signals }),
};

export const detectionsApi = {
  list: (params?: {
    limit?: number;
    offset?: number;
    stage?: string;
    min_confidence?: number;
    sort_by?: string;
  }) => api.get("/detections/", { params }),

  get: (id: string) => api.get(`/detections/${id}`),

  runPipeline: (windowHours?: number) =>
    api.post(`/detections/run-pipeline?window_hours=${windowHours || 24}`),

  stagesSummary: () => api.get("/detections/stages/summary"),
};

export const searchApi = {
  search: (query: string, limit?: number) =>
    api.get("/search/", { params: { q: query, limit } }),
};
