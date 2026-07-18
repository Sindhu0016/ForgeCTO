import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@clerk/react";
import { isClerkConfigured } from "../lib/clerk";

function ClerkProtectedRoute() {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return (
      <div className="page">
        <div className="atmosphere" aria-hidden />
        <p className="muted auth-loading">Checking session…</p>
      </div>
    );
  }

  if (!isSignedIn) {
    return <Navigate to="/sign-in" replace />;
  }

  return <Outlet />;
}

export function ProtectedRoute() {
  if (!isClerkConfigured) {
    return <Outlet />;
  }

  return <ClerkProtectedRoute />;
}
