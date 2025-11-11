import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import './Activities.css'

export default function Activities() {
  const [activities, setActivities] = useState([])
  const [filteredActivities, setFilteredActivities] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [dateFilter, setDateFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadActivities()
  }, [])

  useEffect(() => {
    filterActivities()
  }, [searchQuery, dateFilter, activities])

  async function loadActivities() {
    try {
      const response = await fetch('/activity_log.json')
      const data = await response.json()
      const allActivities = (data.activities || []).reverse() // Most recent first
      setActivities(allActivities)
      setFilteredActivities(allActivities)
      setLoading(false)
    } catch (err) {
      console.error('Failed to load activities:', err)
      setLoading(false)
    }
  }

  function filterActivities() {
    let filtered = activities

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(a =>
        a.activity_description?.toLowerCase().includes(query)
      )
    }

    // Filter by date
    if (dateFilter) {
      filtered = filtered.filter(a =>
        a.timestamp?.startsWith(dateFilter)
      )
    }

    setFilteredActivities(filtered)
  }

  if (loading) {
    return <div className="loading">Loading activities...</div>
  }

  return (
    <div className="page activities-page">
      <div className="page-header">
        <h1>Activities</h1>
        <p>Browse and search your activity history</p>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="filters">
          <div className="filter-item">
            <input
              type="text"
              className="search-input"
              placeholder="Search activities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="filter-item">
            <input
              type="date"
              className="date-input"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
            />
          </div>

          <button
            className="btn btn-secondary"
            onClick={() => {
              setSearchQuery('')
              setDateFilter('')
            }}
          >
            Clear Filters
          </button>

          <div className="filter-info">
            Showing {filteredActivities.length} of {activities.length} activities
          </div>
        </div>
      </div>

      {/* Activities List */}
      {filteredActivities.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>No activities found</p>
            {(searchQuery || dateFilter) && (
              <p className="text-sm">Try adjusting your filters</p>
            )}
          </div>
        </div>
      ) : (
        <div className="activities-grid">
          {filteredActivities.map((activity, index) => (
            <div key={index} className="activity-card">
              <div className="activity-header">
                <div className="activity-timestamp">
                  {activity.timestamp && format(new Date(activity.timestamp), 'PPpp')}
                </div>
                <div className={`activity-badge ${activity.analysis_successful ? 'success' : 'failed'}`}>
                  {activity.analysis_successful ? 'Success' : 'Failed'}
                </div>
              </div>

              <div className="activity-body">
                <p className="activity-text">
                  {activity.activity_description || 'No description available'}
                </p>

                {activity.screenshot_path && (
                  <div className="activity-screenshot">
                    <img
                      src={`/${activity.screenshot_path}`}
                      alt="Screenshot"
                      onError={(e) => {
                        e.target.style.display = 'none'
                      }}
                    />
                  </div>
                )}

                {activity.confidence && (
                  <div className="activity-meta">
                    <span className="meta-label">Confidence:</span>
                    <span className="meta-value">{activity.confidence}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
