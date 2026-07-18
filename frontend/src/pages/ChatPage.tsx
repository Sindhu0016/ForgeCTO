import { Link } from "react-router-dom";
import { AuthHeaderActions } from "../components/AuthHeaderActions";
import { GeneralChat } from "../components/GeneralChat";

export function ChatPage() {
  return (
    <div className="page chat-page">
      <div className="atmosphere subtle" aria-hidden />
      <header className="dash-header">
        <Link className="brand-link" to="/">
          ForgeCTO
        </Link>
        <div className="dash-meta">
          <Link className="btn secondary auth-nav-btn" to="/">
            Home
          </Link>
          <AuthHeaderActions />
        </div>
      </header>
      <main className="chat-page-main">
        <h1 className="chat-page-title">General assistant</h1>
        <p className="muted chat-page-lead">
          Open-ended help for stacks, MVP scope, architecture, and founder questions. For answers
          grounded in a generated CTO pack, open a project and use Ask the CTO.
        </p>
        <GeneralChat embedded />
      </main>
    </div>
  );
}
