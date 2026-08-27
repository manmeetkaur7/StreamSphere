const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const INTERNAL_API_BASE_URL =
  process.env.INTERNAL_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export const API_BASE_URL = PUBLIC_API_BASE_URL;

async function responseError(response: Response, fallback: string) {
  const payload = await response.json().catch(() => null);
  return payload?.detail ?? payload?.error?.message ?? fallback;
}

export function resolveApiBaseUrl() {
  return typeof window === "undefined" ? INTERNAL_API_BASE_URL : PUBLIC_API_BASE_URL;
}

const ACCESS_TOKEN_KEY = "streamsphere_access_token";

export function getAccessToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function saveAccessToken(accessToken: string) {
  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
}

export function clearAccessToken() {
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export async function loginWithCredentials(identifier: string, password: string) {
  const body = new URLSearchParams();
  body.set("username", identifier);
  body.set("password", password);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });
  } catch {
    throw new Error("Unable to reach StreamSphere. Verify that the API is running and try again.");
  }

  if (!response.ok) {
    throw new Error(await responseError(response, "Unable to sign in."));
  }

  const payload = await response.json().catch(() => null);

  saveAccessToken(String(payload.access_token ?? ""));
}

export async function registerAndLogin(username: string, email: string, password: string) {
  let registerResponse: Response;
  try {
    registerResponse = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });
  } catch {
    throw new Error("Unable to reach StreamSphere. Verify that the API is running and try again.");
  }

  if (!registerResponse.ok) {
    throw new Error(await responseError(registerResponse, "Unable to create account."));
  }

  await loginWithCredentials(email, password);
}

export async function fetchWithAuth<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAccessToken();
  if (!token) {
    throw new Error("Please sign in to continue.");
  }

  let response: Response;
  try {
    response = await fetch(`${resolveApiBaseUrl()}${path}`, {
      ...init,
      headers: {
        ...(init?.headers ?? {}),
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
  } catch {
    throw new Error("Unable to reach StreamSphere. Verify that the API is running and try again.");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    throw new Error(await responseError(response, "Request failed."));
  }

  return (await response.json()) as T;
}
