/**
 * Foresight — API Client
 * Axios instance with interceptors for auth tokens and error handling.
 */

import axios from "axios";
import { useAuthStore } from "@/store/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 — try refresh, else logout
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE}/api/v1/auth/refresh`, null, {
            params: { refresh_token: refreshToken },
          });
          const { access_token, refresh_token } = res.data;
          const user = useAuthStore.getState().user;
          if (user) {
            useAuthStore.getState().setAuth(user, access_token, refresh_token);
          }
          original.headers.Authorization = `Bearer ${access_token}`;
          return api(original);
        } catch {
          useAuthStore.getState().clearAuth();
        }
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth API ──

export const authAPI = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post("/auth/register", data),

  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),

  getProfile: () => api.get("/auth/me"),
};

// ── Signals API ──

export const signalsAPI = {
  ingest: (data: { text: string; platform: string; author?: string; url?: string }) =>
    api.post("/signals/ingest", data),

  list: (params?: { limit?: number; offset?: number; platform?: string }) =>
    api.get("/signals/", { params }),

  getById: (id: string) => api.get(`/signals/${id}`),
};
