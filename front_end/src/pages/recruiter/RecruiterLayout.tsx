import { Route, Routes } from "react-router-dom";
import RecruiterDashboard from "./Dashboard";

/**
 * Layout shell for recruiter routes. Owns recruiter-specific routing and sidebar/nav.
 */
export function RecruiterLayout() {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <Routes>
        <Route index element={<RecruiterDashboard />} />
      </Routes>
    </div>
  );
}
