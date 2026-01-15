import { Navigate, Outlet } from "react-router-dom";
import { getToken } from "../utils/auth";

// Protector de rutes
export default function ProtectedRoute() {
  const token = getToken();
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}
