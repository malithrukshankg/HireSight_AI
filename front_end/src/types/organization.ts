export type PlanType = "free" | "pro" | "enterprise";

export type Organization = {
  id: string;
  name: string;
  plan: PlanType;
  created_at: string;
  updated_at: string;
};

export type OrganizationUpdate = {
  name?: string;
  plan?: PlanType;
};
