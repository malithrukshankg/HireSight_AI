import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../components/layout/AppLayout";
import { ProtectedRoute } from "../components/layout/ProtectedRoute";
import { RoleGuard } from "../components/layout/RoleGuard";
import { RoleRedirect } from "../components/layout/RoleRedirect";
import Login from "../pages/Login";
import ChooseRole from "../pages/ChooseRole";
import { AdminLayout } from "../pages/admin/AdminLayout";
import { RecruiterLayout } from "../pages/recruiter/RecruiterLayout";
import { CandidateLayout } from "../pages/candidate/CandidateLayout";

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      {
        path: "/login",
        element: <Login />,
      },
      {
        path: "/",
        element: <ProtectedRoute />,
        children: [
          {
            index: true,
            element: <RoleRedirect />,
          },
          {
            path: "role",
            element: <ChooseRole />,
          },
          {
            path: "admin",
            element: <RoleGuard allowedRoles={["admin"]} />,
            children: [{ index: true, element: <AdminLayout /> }],
          },
          {
            path: "recruiter",
            element: <RoleGuard allowedRoles={["recruiter"]} />,
            children: [{ index: true, element: <RecruiterLayout /> }],
          },
          {
            path: "candidate",
            element: <RoleGuard allowedRoles={["candidate"]} />,
            children: [{ index: true, element: <CandidateLayout /> }],
          },
        ],
      },
    ],
  },
]);
