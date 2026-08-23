import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LoadingState } from "./Feedback";

export function PublicRoute({ children }) {
  const { loading, isAuthenticated } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingState message="Checking session…" />;
  }

  if (isAuthenticated) {
    const next =
      new URLSearchParams(location.search).get("next") || "/";

    return <Navigate to={next} replace />;
  }

  return children;
}