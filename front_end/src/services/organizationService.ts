import { API_BASE_URL } from "../utils/config";
import type { Organization, OrganizationUpdate } from "../types/organization";

/**
 * Fetch organizations linked to the current user via RecruiterOrganization.
 */
export async function getOrganizationsForCurrentUser(
  accessToken: string
): Promise<Organization[]> {
  const response = await fetch(`${API_BASE_URL}/organizations/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(
      `Fetch organizations failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<Organization[]>;
}

/**
 * Update an organization by ID.
 */
export async function updateOrganization(
  accessToken: string,
  id: string,
  payload: OrganizationUpdate
): Promise<Organization> {
  const response = await fetch(`${API_BASE_URL}/organizations/${id}`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(
      (err as { detail?: string }).detail ||
        `Update organization failed: ${response.status}`
    );
  }

  return response.json() as Promise<Organization>;
}

/**
 * Delete an organization by ID.
 */
export async function deleteOrganization(
  accessToken: string,
  id: string
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/organizations/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(
      (err as { detail?: string }).detail ||
        `Delete organization failed: ${response.status}`
    );
  }
}
