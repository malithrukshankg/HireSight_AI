import { API_BASE_URL } from "../utils/config";
import type { CVProfile } from "../types/cv";

export async function getCvProfile(
  accessToken: string,
  cvId: string
): Promise<CVProfile> {
  const response = await fetch(`${API_BASE_URL}/cv/${cvId}/profile`, {
    method: "GET",
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
        `Fetch CV profile failed: ${response.status}`
    );
  }

  return response.json() as Promise<CVProfile>;
}

export async function openCvPdfInNewTab(
  accessToken: string,
  cvId: string
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/cv/${cvId}/file`, {
    method: "GET",
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
        `Fetch CV file failed: ${response.status}`
    );
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const openedWindow = window.open(objectUrl, "_blank", "noopener,noreferrer");
  if (!openedWindow) {
    URL.revokeObjectURL(objectUrl);
    throw new Error("Popup blocked while opening CV PDF");
  }

  // Keep URL alive long enough for browser to load document.
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
}

