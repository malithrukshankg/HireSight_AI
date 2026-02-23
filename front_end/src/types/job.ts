export type JobStatus = "draft" | "open" | "closed";

export type Job = {
  id: string;
  organization_id: string;
  created_by_user_id: string;
  title: string;
  description: string;
  location: string;
  employment_type: string;
  status: JobStatus;
  requirements_json: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type JobCreate = {
  organization_id: string;
  title: string;
  description: string;
  location: string;
  employment_type: string;
  status?: JobStatus;
  requirements_json?: Record<string, unknown>;
};

export type JobUpdate = {
  title?: string;
  description?: string;
  location?: string;
  employment_type?: string;
  status?: JobStatus;
  requirements_json?: Record<string, unknown>;
};
