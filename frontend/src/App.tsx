import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { GlobalChatWidget } from "./components/GlobalChatWidget";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ChatPage } from "./pages/ChatPage";
import { Home } from "./pages/Home";
import { ProjectDashboard } from "./pages/ProjectDashboard";
import { SignInPage } from "./pages/SignInPage";
import { SignUpPage } from "./pages/SignUpPage";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/sign-in/*" element={<SignInPage />} />
        <Route path="/sign-up/*" element={<SignUpPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/projects/:id" element={<ProjectDashboard />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <GlobalChatWidget />
    </BrowserRouter>
  );
}
