import { Route, Routes } from "react-router-dom";
import CandidateDashboard from "./Dashboard";

/**
 * Layout shell for candidate routes. Owns candidate-specific routing and sidebar/nav.
 */
export function CandidateLayout() {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <Routes>
        <Route index element={<CandidateDashboard />} />
      </Routes>
    </div>
  );
}
