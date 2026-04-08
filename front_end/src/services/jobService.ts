import { API_BASE_URL } from "../utils/config";
import type {
  Job,
  JobApplyPayload,
  JobApplyResponse,
  JobCreate,
  JobUpdate,
} from "../types/job";
import type { JobApplication as JobApplicationListItem } from "../types/application";

/**
 * Fetch jobs created by the current user (recruiter).
 */
export async function getMyJobs(accessToken: string): Promise<Job[]> {
  const response = await fetch(`${API_BASE_URL}/jobs/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(
      `Fetch jobs failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<Job[]>;
}

/**
 * Fetch jobs with optional filters and pagination.
 */
export async function getJobs(
  accessToken: string,
  params?: {
    organization_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
    query?: string;
    location?: string;
    sort?: "recent";
  }
): Promise<Job[]> {
  const searchParams = new URLSearchParams();
  if (params?.organization_id) searchParams.set("organization_id", params.organization_id);
  if (params?.status) searchParams.set("status", params.status);
  if (params?.page != null) searchParams.set("page", String(params.page));
  if (params?.page_size != null) searchParams.set("page_size", String(params.page_size));
  if (params?.query) searchParams.set("query", params.query);
  if (params?.location) searchParams.set("location", params.location);
  if (params?.sort) searchParams.set("sort", params.sort);

  const query = searchParams.toString();
  const url = query ? `${API_BASE_URL}/jobs?${query}` : `${API_BASE_URL}/jobs`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(
      `Fetch jobs failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json() as Promise<Job[]>;
}

/**
 * Fetch a single job by ID.
 */
export async function getJobById(
  accessToken: string,
  id: string
): Promise<Job> {
  const response = await fetch(`${API_BASE_URL}/jobs/${id}`, {
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
        `Fetch job failed: ${response.status}`
    );
  }

  return response.json() as Promise<Job>;
}

/**
 * Create a new job. User must be a member of the organization.
 */
export async function createJob(
  accessToken: string,
  payload: JobCreate
): Promise<Job> {
  const body: Record<string, unknown> = {
    organization_id: payload.organization_id,
    title: payload.title,
    description: payload.description,
    location: payload.location,
    employment_type: payload.employment_type,
    status: payload.status ?? "draft",
  };
  if (payload.requirements_json != null) {
    body.requirements_json = payload.requirements_json;
  }

  const response = await fetch(`${API_BASE_URL}/jobs`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(
      (err as { detail?: string }).detail ||
        `Create job failed: ${response.status}`
    );
  }

  return response.json() as Promise<Job>;
}

/**
 * Update a job by ID. User must be a member of the job's organization.
 */
export async function updateJob(
  accessToken: string,
  id: string,
  payload: JobUpdate
): Promise<Job> {
  const response = await fetch(`${API_BASE_URL}/jobs/${id}`, {
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
        `Update job failed: ${response.status}`
    );
  }

  return response.json() as Promise<Job>;
}

/**
 * Delete a job by ID. User must be a member of the job's organization.
 */
export async function deleteJob(
  accessToken: string,
  id: string
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/jobs/${id}`, {
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
        `Delete job failed: ${response.status}`
    );
  }
}

export async function applyToJob(
  accessToken: string,
  id: string,
  payload: JobApplyPayload
): Promise<JobApplyResponse> {
  const formData = new FormData();
  formData.append("full_name", payload.full_name);
  formData.append("email", payload.email);
  if (payload.phone && payload.phone.trim() !== "") {
    formData.append("phone", payload.phone.trim());
  }
  if (payload.cv_file) {
    formData.append("cv_file", payload.cv_file);
  }

  const response = await fetch(`${API_BASE_URL}/jobs/${id}/apply`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(
      (err as { detail?: string }).detail || `Apply failed: ${response.status}`
    );
  }

  return response.json() as Promise<JobApplyResponse>;
}

export async function getJobApplications(
  accessToken: string,
  id: string
): Promise<JobApplicationListItem[]> {
  const response = await fetch(`${API_BASE_URL}/jobs/${id}/applications`, {
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
        `Fetch applications failed: ${response.status}`
    );
  }

  return response.json() as Promise<JobApplicationListItem[]>;
}
