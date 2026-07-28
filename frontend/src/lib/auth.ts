import { apiFetch } from "./api";

export type AuthUser = {
  id: string;
  email: string;
  display_name: string;
  created_at: string;
};

type AuthResponse = {
  user: AuthUser;
  access_expires_in_seconds: number;
};

export function currentUser(): Promise<AuthUser> {
  return apiFetch<AuthUser>("/auth/me");
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function register(
  displayName: string,
  email: string,
  password: string,
): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      display_name: displayName,
      email,
      password,
    }),
  });
}

export async function logout(): Promise<void> {
  await apiFetch<void>("/auth/logout", { method: "POST" });
}
