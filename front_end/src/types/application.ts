export type JobApplication = {
  candidate_id: string;
  job_id: string;
  organization_id: string;
  full_name: string;
  email: string;
  phone: string | null;
  status: string;
  applied_at: string;
  cv_id: string | null;
};

