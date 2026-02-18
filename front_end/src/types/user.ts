/** Response shape from POST /user/upsert (backend userCreate schema). */
export type UpsertUserResponse = {
  id: number;
  name?: string;
  email: string;
  auth0_sub?: string;
  role: "admin" | "recruiter" | "candidate";
};
