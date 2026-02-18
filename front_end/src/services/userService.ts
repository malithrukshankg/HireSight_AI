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
