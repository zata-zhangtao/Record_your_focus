import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { format, formatDistanceToNow } from 'date-fns'
import './Dashboard.css'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [recentActivities, setRecentActivities] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDashboardData()
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  async function loadDashboardData() {
    try {
      // Load from local activity_log.json
      // In production, this would be an API call
      const response = await fetch('/activity_log.json')
      const data = await response.json()

      const activities = data.activities || []

      // Calculate statistics
      const total = activities.length
      const successful = activities.filter(a => a.analysis_successful).length
      const failed = total - successful
      const successRate = total > 0 ? (successful / total * 100).toFixed(1) : 0

      setStats({
        total_activities: total,
        successful_analyses: successful,
        failed_analyses: failed,
        success_rate: parseFloat(successRate),
        first_activity: activities[0]?.timestamp,
        last_activity: activities[activities.length - 1]?.timestamp
      })

      // Get last 5 activities
      setRecentActivities(activities.slice(-5).reverse())
      setLoading(false)

    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('Failed to load dashboard data. Make sure the application is running.')
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  if (error) {
    return (
      <div className="page">
        <div className="error">{error}</div>
      </div>
    )
  }

  return (
    <div className="page dashboard-page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your activity recording</p>
      </div>

      {/* Statistics Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#E3F2FD' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="#2196F3" strokeWidth="2"/>
              <path d="M3 9h18M9 3v18" stroke="#2196F3" strokeWidth="2"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats?.total_activities || 0}</div>
            <div className="stat-label">Total Activities</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#E8F5E9' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M20 6L9 17l-5-5" stroke="#4CAF50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats?.successful_analyses || 0}</div>
            <div className="stat-label">Successful</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#FFEBEE' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6l12 12" stroke="#f44336" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats?.failed_analyses || 0}</div>
            <div className="stat-label">Failed</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#FFF3E0' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="#FF9800" strokeWidth="2"/>
              <path d="M12 8v4M12 16h.01" stroke="#FF9800" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats?.success_rate || 0}%</div>
            <div className="stat-label">Success Rate</div>
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="card">
        <div className="card-header">
          <h2>Recent Activities</h2>
          <Link to="/activities" className="btn btn-secondary btn-sm">View All</Link>
        </div>

        {recentActivities.length === 0 ? (
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="30" stroke="currentColor" strokeWidth="2"/>
              <path d="M32 20v16M32 44h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <p>No activities recorded yet</p>
            <p className="text-sm">Start recording to see your activities here</p>
          </div>
        ) : (
          <div className="activities-list">
            {recentActivities.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-time">
                  {activity.timestamp && formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                </div>
                <div className="activity-description">
                  {activity.activity_description || 'No description'}
                </div>
                <div className={`activity-status ${activity.analysis_successful ? 'success' : 'failed'}`}>
                  {activity.analysis_successful ? '✓' : '✗'}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <Link to="/time-query" className="action-card">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="12" stroke="currentColor" strokeWidth="2"/>
            <path d="M16 10v6l4 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <h3>Time Query</h3>
          <p>Analyze activities in a specific time range</p>
        </Link>

        <Link to="/activities" className="action-card">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <path d="M5 8h22M5 16h22M5 24h22" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <h3>Browse Activities</h3>
          <p>View and search your activity history</p>
        </Link>

        <Link to="/settings" className="action-card">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="3" stroke="currentColor" strokeWidth="2"/>
            <path d="M22 16a6 6 0 0 1-2 4.5M10 16a6 6 0 0 0 2 4.5M16 10a6 6 0 0 1 4.5 2M16 22a6 6 0 0 0 4.5-2"
                  stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <h3>Settings</h3>
          <p>Configure recording and API settings</p>
        </Link>
      </div>
    </div>
  )
}
