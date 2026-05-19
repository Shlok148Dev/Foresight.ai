import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "./auth";

describe("AuthStore", () => {
  beforeEach(() => {
    useAuthStore.getState().clearAuth();
  });

  it("starts with null user and no auth", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.accessToken).toBeNull();
  });

  it("sets auth correctly", () => {
    const mockUser = {
      id: "123", email: "test@foresight.ai", username: "testuser",
      full_name: "Test", role: "free", is_active: true,
      is_verified: false, created_at: "2026-01-01",
    };
    useAuthStore.getState().setAuth(mockUser, "access-tok", "refresh-tok");

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.email).toBe("test@foresight.ai");
    expect(state.accessToken).toBe("access-tok");
    expect(state.refreshToken).toBe("refresh-tok");
  });

  it("clears auth correctly", () => {
    useAuthStore.getState().setAuth(
      { id: "1", email: "a@b.c", username: "u", full_name: null, role: "free", is_active: true, is_verified: false, created_at: "" },
      "tok", "ref"
    );
    useAuthStore.getState().clearAuth();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
  });

  it("sets loading state", () => {
    useAuthStore.getState().setLoading(true);
    expect(useAuthStore.getState().isLoading).toBe(true);
    useAuthStore.getState().setLoading(false);
    expect(useAuthStore.getState().isLoading).toBe(false);
  });
});
