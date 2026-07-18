import { Link } from "react-router-dom";

export function ClerkSetupPage({ mode }: { mode: "sign-in" | "sign-up" }) {
  const title = mode === "sign-in" ? "Sign in" : "Sign up";

  return (
    <div className="page auth-page">
      <div className="atmosphere" aria-hidden />
      <header className="site-header auth-header">
        <p className="brand">ForgeCTO</p>
      </header>
      <main className="auth-main auth-setup">
        <h1 className="brand-hero auth-brand">ForgeCTO</h1>
        <p className="tagline auth-tagline">
          {title} needs a Clerk publishable key before it can load.
        </p>
        <ol className="auth-setup-steps">
          <li>
            Open{" "}
            <a href="https://dashboard.clerk.com/~/api-keys" target="_blank" rel="noreferrer">
              Clerk API Keys
            </a>
          </li>
          <li>
            Copy your <strong>Publishable Key</strong> (<code>pk_test_…</code>)
          </li>
          <li>
            Paste it into <code>frontend/.env.local</code> as{" "}
            <code>VITE_CLERK_PUBLISHABLE_KEY=…</code>
          </li>
          <li>Restart the Vite dev server</li>
        </ol>
        <Link className="btn primary" to="/">
          Back to home
        </Link>
      </main>
    </div>
  );
}
