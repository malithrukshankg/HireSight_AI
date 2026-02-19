import { API_BASE_URL } from "../utils/config";
import type { UpsertUserResponse } from "../types/user";

/**
 * Call POST /user/upsert with the Auth0 access token.
 * Backend reads email, sub, role from the JWT and creates or updates the user.
 */
export async function upsertUser(
  accessToken: string
): Promise<UpsertUserResponse> {
  const response = await fetch(`${API_BASE_URL}/user/upsert`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(
      `Upsert user failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<UpsertUserResponse>;
}

/**
 * Switch current user's role (candidate <-> recruiter) via Auth0 Management API.
 * After success, call getAccessTokenSilently({ ignoreCache: true }) to get a new token
 * with updated role — the JWT is issued at login and does not update until refresh/re-login.
 */
export async function switchRole(
  accessToken: string,
  role: "candidate" | "recruiter"
): Promise<{ message: string; role: string }> {
  const response = await fetch(`${API_BASE_URL}/me/switch-role`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ role }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error((err as { detail?: string }).detail || `Switch role failed: ${response.status}`);
  }

  return response.json() as Promise<{ message: string; role: string }>;
}
