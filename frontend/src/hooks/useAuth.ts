/**
 * Foresight — useAuth Hook wrapper
 * =================================
 * Integrates auth store state with API login, register, and token management.
 */

"use client";

import { useState } from "react";
import { useAuthStore } from "@/store/auth";
import { authApi } from "@/lib/api";

export function useAuth() {
  const store = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  const login = async (email: string, password: string) => {
    store.setLoading(true);
    setError(null);
    try {
      const res = await authApi.login(email, password);
      const { access_token, refresh_token, user } = res.data;
      
      // Store in Zustand & localstorage
      localStorage.setItem("foresight_token", access_token);
      store.setAuth(user, access_token, refresh_token || "");
      store.setLoading(false);
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Login failed. Check credentials.";
      setError(msg);
      store.setLoading(false);
      throw new Error(msg);
    }
  };

  const register = async (email: string, password: string, username: string, fullName?: string) => {
    store.setLoading(true);
    setError(null);
    try {
      const res = await authApi.register(email, password, username, fullName);
      const { access_token, refresh_token, user } = res.data;

      localStorage.setItem("foresight_token", access_token);
      store.setAuth(user, access_token, refresh_token || "");
      store.setLoading(false);
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Registration failed. Try again.";
      setError(msg);
      store.setLoading(false);
      throw new Error(msg);
    }
  };

  const logout = () => {
    localStorage.removeItem("foresight_token");
    store.clearAuth();
    setError(null);
  };

  const loadUser = async () => {
    const token = localStorage.getItem("foresight_token");
    if (!token) return;
    store.setLoading(true);
    try {
      const res = await authApi.me();
      store.setAuth(res.data, token, store.refreshToken || "");
      store.setLoading(false);
    } catch {
      logout();
      store.setLoading(false);
    }
  };

  return {
    user: store.user,
    token: store.accessToken,
    isLoading: store.isLoading,
    error,
    login,
    register,
    logout,
    loadUser,
    clearError: () => setError(null),
  };
}
