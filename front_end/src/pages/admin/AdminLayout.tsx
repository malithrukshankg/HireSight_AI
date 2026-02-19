import { Route, Routes } from "react-router-dom";
import AdminDashboard from "./Dashboard";

/**
 * Layout shell for admin routes. Owns admin-specific routing and sidebar/nav.
 */
export function AdminLayout() {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <Routes>
        <Route index element={<AdminDashboard />} />
      </Routes>
    </div>
  );
}
