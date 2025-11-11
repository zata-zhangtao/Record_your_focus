import { Outlet, NavLink } from 'react-router-dom'
import './Layout.css'

export default function Layout() {
  return (
    <div className="layout">
      <nav className="sidebar">
        <div className="sidebar-header">
          <svg className="logo" width="32" height="32" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
            <circle cx="12" cy="12" r="3" fill="currentColor"/>
          </svg>
          <h2>Activity Recorder</h2>
        </div>

        <div className="nav-links">
          <NavLink to="/dashboard" className="nav-link">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect x="3" y="3" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
              <rect x="11" y="3" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
              <rect x="3" y="11" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
              <rect x="11" y="11" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            <span>Dashboard</span>
          </NavLink>

          <NavLink to="/activities" className="nav-link">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <span>Activities</span>
          </NavLink>

          <NavLink to="/time-query" className="nav-link">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M10 6v4l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <span>Time Query</span>
          </NavLink>

          <NavLink to="/settings" className="nav-link">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="2" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M14 10a4 4 0 0 1-1.5 3.1M6 10a4 4 0 0 0 1.5 3.1M10 6a4 4 0 0 1 3.1 1.5M10 14a4 4 0 0 0 3.1-1.5"
                    stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <span>Settings</span>
          </NavLink>
        </div>

        <div className="sidebar-footer">
          <p className="version">Version 1.0.0</p>
        </div>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
