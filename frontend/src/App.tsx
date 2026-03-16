import { BrowserRouter, Link, Route, Routes, NavLink, Navigate, useLocation } from 'react-router-dom'
import { AppStateProvider } from './context/AppStateContext'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ResumePage } from './pages/ResumePage'
import { JobsPage } from './pages/JobsPage'
import { ResultsPage } from './pages/ResultsPage'
import { LoginPage } from './pages/LoginPage'
import './App.css'

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

function MainApp() {
  const { isAuthenticated, email, logout } = useAuth()
  
  return (
    <div className="app-root">
      {isAuthenticated && (
        <header className="app-header">
          <div className="brand">
            <Link to="/">SkillGap Analyzer</Link>
          </div>
          <nav className="nav">
            <NavLink to="/" end>Resume</NavLink>
            <NavLink to="/jobs">Jobs</NavLink>
            <NavLink to="/results">Results</NavLink>
            <span style={{ marginLeft: 'auto', marginRight: '1rem', color: '#666' }}>{email}</span>
            <button onClick={logout} className="secondary" style={{ padding: '0.25rem 0.5rem' }}>Logout</button>
          </nav>
        </header>
      )}

      <main className="app-main">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><ResumePage /></ProtectedRoute>} />
          <Route path="/jobs" element={<ProtectedRoute><JobsPage /></ProtectedRoute>} />
          <Route path="/results" element={<ProtectedRoute><ResultsPage /></ProtectedRoute>} />
        </Routes>
      </main>

      <footer className="app-footer">
        <span>Autonomous Skill Gap Analyzer</span>
      </footer>
    </div>
  )
}

function AppShell() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppStateProvider>
          <MainApp />
        </AppStateProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default AppShell
