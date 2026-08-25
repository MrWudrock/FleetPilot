import { getApiBase } from "@/lib/config";

const TOKEN_KEY = "fleetpilot_token";

/**
 * Access token is stored in localStorage for the SPA/Electron shell.
 * Production hardening: move to httpOnly Secure cookies + short-lived access tokens.
 */

export type User = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  organization_id: string;
};

export type Organization = {
  id: string;
  name: string;
  slug: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
  organization: Organization;
};

export type MeResponse = {
  user: User;
  organization: Organization;
};

function parseApiError(detail: unknown, fallback: string): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (typeof item === "object" && item && "msg" in item ? String(item.msg) : String(item)))
      .join(", ");
  }
  return fallback;
}

async function readApiError(response: Response, fallback: string): Promise<string> {
  const error = await response.json().catch(() => ({}));
  return parseApiError(error.detail, fallback);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export async function signup(payload: {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
}): Promise<AuthResponse> {
  const response = await fetch(`${getApiBase()}/api/v1/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await readApiError(response, "Registration failed"));
  }

  const data: AuthResponse = await response.json();
  setToken(data.access_token);
  return data;
}

export async function login(payload: { email: string; password: string }): Promise<AuthResponse> {
  const response = await fetch(`${getApiBase()}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await readApiError(response, "Login failed"));
  }

  const data: AuthResponse = await response.json();
  setToken(data.access_token);
  return data;
}

export async function acceptInvite(payload: {
  token: string;
  password: string;
}): Promise<AuthResponse> {
  const response = await fetch(`${getApiBase()}/api/v1/auth/accept-invite`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await readApiError(response, "Invite acceptance failed"));
  }

  const data: AuthResponse = await response.json();
  setToken(data.access_token);
  return data;
}

export async function fetchMe(): Promise<MeResponse> {
  const token = getToken();
  if (!token) throw new Error("Not authenticated");

  const response = await fetch(`${getApiBase()}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    if (response.status === 401) clearToken();
    throw new Error("Session expired");
  }

  return response.json();
}

export function logout(): void {
  clearToken();
  window.location.href = "/login";
}
