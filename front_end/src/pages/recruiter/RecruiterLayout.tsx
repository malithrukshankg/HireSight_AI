import { NavLink, Route, Routes } from "react-router-dom";
import RecruiterDashboard from "./Dashboard";
import JobApplicationsPage from "./JobApplications";

/**
 * Layout shell for recruiter routes. Owns recruiter-specific routing and sidebar/nav.
 */
export function RecruiterLayout() {
  return (
    <div className="flex min-h-0 flex-1 overflow-hidden">
      {/* Sidebar - uses left space, full height */}
      <aside className="hidden w-56 shrink-0 border-r border-white/10 bg-black/20 lg:block">
        <div className="border-b border-white/10 px-4 py-5">
          <span className="text-lg font-semibold text-white">Recruiter</span>
        </div>
        <nav className="flex flex-col gap-1 p-4">
          <NavLink
            to="/recruiter"
            end
            className={({ isActive }) =>
              `rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${
                isActive ? "bg-accent/80 text-white" : "text-white/80 hover:bg-white/10 hover:text-white"
              }`
            }
          >
            Dashboard
          </NavLink>
        </nav>
      </aside>
      {/* Main content - fills remaining width */}
      <div className="min-w-0 flex-1 overflow-auto">
        <Routes>
          <Route index element={<RecruiterDashboard />} />
          <Route path="jobs/:jobId/applications" element={<JobApplicationsPage />} />
        </Routes>
      </div>
    </div>
  );
}
