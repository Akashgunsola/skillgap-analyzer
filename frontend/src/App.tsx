import { BrowserRouter, Link, Route, Routes, NavLink } from 'react-router-dom'
import { AppStateProvider } from './context/AppStateContext'
import { ResumePage } from './pages/ResumePage'
import { JobsPage } from './pages/JobsPage'
import { ResultsPage } from './pages/ResultsPage'
import './App.css'

function AppShell() {
  return (
    <BrowserRouter>
      <AppStateProvider>
        <div className="app-root">
          <header className="app-header">
            <div className="brand">
              <Link to="/">SkillGap Analyzer</Link>
            </div>
            <nav className="nav">
              <NavLink to="/" end>
                Resume
              </NavLink>
              <NavLink to="/jobs">Jobs</NavLink>
              <NavLink to="/results">Results</NavLink>
            </nav>
          </header>

          <main className="app-main">
            <Routes>
              <Route path="/" element={<ResumePage />} />
              <Route path="/jobs" element={<JobsPage />} />
              <Route path="/results" element={<ResultsPage />} />
            </Routes>
          </main>

          <footer className="app-footer">
            <span>Autonomous Skill Gap Analyzer</span>
          </footer>
        </div>
      </AppStateProvider>
    </BrowserRouter>
  )
}

export default AppShell
