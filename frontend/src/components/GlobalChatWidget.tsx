import { useLocation } from "react-router-dom";
import { GeneralChat } from "./GeneralChat";

/** Floating assistant on app pages; hidden on auth and the full /chat page. */
export function GlobalChatWidget() {
  const { pathname } = useLocation();
  if (
    pathname.startsWith("/sign-in") ||
    pathname.startsWith("/sign-up") ||
    pathname === "/chat"
  ) {
    return null;
  }
  return <GeneralChat />;
}
