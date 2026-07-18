import { Show, UserButton } from "@clerk/react";
import { Link } from "react-router-dom";
import { isClerkConfigured } from "../lib/clerk";

export function AuthHeaderActions() {
  return (
    <div className="auth-header-actions">
      <Link className="btn secondary auth-nav-btn" to="/chat">
        Chat
      </Link>
      {isClerkConfigured && (
        <>
          <Show when="signed-out">
            <Link className="btn secondary auth-nav-btn" to="/sign-in">
              Sign in
            </Link>
          </Show>
          <Show when="signed-in">
            <UserButton />
          </Show>
        </>
      )}
    </div>
  );
}
