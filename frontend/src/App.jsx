import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import AppLayout from './layouts/AppLayout'
import AgentSetupPage from './pages/AgentSetupPage'
import AuthPage from './pages/AuthPage'
import ChatPage from './pages/ChatPage'
import DashboardPage from './pages/DashboardPage'
import DomainPage from './pages/DomainPage'
import NotFoundPage from './pages/NotFoundPage'
import ProfilePage from './pages/ProfilePage'
import SettingsPage from './pages/SettingsPage'
import { LoadingScreen } from './components/ui'

function ProtectedRoute({ children }) {
  const { isAuthenticated, initializing } = useAuth()
  const location = useLocation()

  if (initializing) return <LoadingScreen label="Restoring your session…" />
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location }} />
  return children
}

function PublicOnlyRoute({ children }) {
  const { isAuthenticated, initializing } = useAuth()
  if (initializing) return <LoadingScreen />
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <AuthPage mode="login" />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/signup"
        element={
          <PublicOnlyRoute>
            <AuthPage mode="signup" />
          </PublicOnlyRoute>
        }
      />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        {/* Level 1: domains. Level 2: the agents inside one domain. */}
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/domain/:domain" element={<DomainPage />} />
        {/* Agent keys contain a dot (marketing.post-image) — a single segment. */}
        <Route path="/agent/:agentKey" element={<ChatPage />} />
        <Route path="/agent/:agentKey/setup" element={<AgentSetupPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
