import { SignUp, useAuth } from "@clerk/react";
import { Link, Navigate } from "react-router-dom";
import { isClerkConfigured } from "../lib/clerk";
import { ClerkSetupPage } from "./ClerkSetupPage";

const clerkAppearance = {
  variables: {
    colorPrimary: "#e2a15c",
    colorBackground: "#162925",
    colorText: "#f2efe6",
    colorTextSecondary: "#b7c4be",
    colorInputBackground: "rgba(255, 255, 255, 0.04)",
    colorInputText: "#f2efe6",
    colorNeutral: "#b7c4be",
    borderRadius: "0.35rem",
    fontFamily: '"IBM Plex Sans", sans-serif',
  },
  elements: {
    card: {
      background: "rgba(15, 31, 28, 0.85)",
      border: "1px solid rgba(242, 239, 230, 0.14)",
      boxShadow: "none",
    },
    headerTitle: {
      fontFamily: '"Fraunces", Georgia, serif',
    },
    formButtonPrimary: {
      background: "#e2a15c",
      color: "#1a1208",
      "&:hover": {
        background: "#ebb06d",
      },
    },
    footerActionLink: {
      color: "#e2a15c",
    },
  },
};

function ClerkSignUpPage() {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return (
      <div className="page">
        <div className="atmosphere" aria-hidden />
        <p className="muted auth-loading">Loading…</p>
      </div>
    );
  }

  if (isSignedIn) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="page auth-page">
      <div className="atmosphere" aria-hidden />
      <header className="site-header auth-header">
        <Link className="brand-link" to="/">
          ForgeCTO
        </Link>
      </header>
      <main className="auth-main">
        <h1 className="brand-hero auth-brand">ForgeCTO</h1>
        <p className="tagline auth-tagline">Create an account to start building.</p>
        <div className="auth-clerk">
          <SignUp
            routing="path"
            path="/sign-up"
            signInUrl="/sign-in"
            fallbackRedirectUrl="/"
            appearance={clerkAppearance}
          />
        </div>
      </main>
    </div>
  );
}

export function SignUpPage() {
  if (!isClerkConfigured) {
    return <ClerkSetupPage mode="sign-up" />;
  }

  return <ClerkSignUpPage />;
}
