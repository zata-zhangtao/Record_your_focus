import { useState } from 'react'
import { format } from 'date-fns'
import './TimeQuery.css'

export default function TimeQuery() {
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [query, setQuery] = useState('总结这段时间的活动')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [hourlyDate, setHourlyDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [selectedHour, setSelectedHour] = useState(null)

  const hourlyPresetHours = Array.from({ length: 16 }, (_, idx) => 9 + idx)

  function formatDateTimeLocal(date) {
    return format(date, "yyyy-MM-dd'T'HH:mm")
  }

  function handleHourlyPreset(hour) {
    const baseDateString = hourlyDate || format(new Date(), 'yyyy-MM-dd')
    const baseDate = new Date(`${baseDateString}T00:00`)

    if (Number.isNaN(baseDate.getTime())) {
      setError('Please select a valid date for hourly query')
      return
    }

    const start = new Date(baseDate)
    if (hour === 24) {
      start.setDate(start.getDate() + 1)
      start.setHours(0, 0, 0, 0)
    } else {
      start.setHours(hour, 0, 0, 0)
    }

    const end = new Date(start)
    end.setHours(end.getHours() + 1)

    setStartTime(formatDateTimeLocal(start))
    setEndTime(formatDateTimeLocal(end))
    setSelectedHour(hour)
    setResult(null)
    setError(null)
  }

  async function handleQuery() {
    if (!startTime || !endTime) {
      setError('Please select both start and end time')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Load activities from file
      const response = await fetch('/activity_log.json')
      const data = await response.json()
      const activities = data.activities || []

      // Filter by time range
      const filtered = activities.filter(a => {
        const timestamp = new Date(a.timestamp)
        return timestamp >= new Date(startTime) && timestamp <= new Date(endTime)
      })

      if (filtered.length === 0) {
        setResult({
          summary: 'No activities found in this time range',
          activities_count: 0,
          activities: []
        })
        setLoading(false)
        return
      }

      // Create summary
      const summary = `Found ${filtered.length} activities in the selected time range. Here's what you did:\n\n` +
        filtered.map(a => `• ${format(new Date(a.timestamp), 'HH:mm')}: ${a.activity_description}`).join('\n')

      setResult({
        summary,
        activities_count: filtered.length,
        activities: filtered,
        time_range: {
          start: startTime,
          end: endTime
        }
      })

    } catch (err) {
      console.error('Query failed:', err)
      setError('Failed to query activities: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page time-query-page">
      <div className="page-header">
        <h1>Time Query</h1>
        <p>Analyze your activities within a specific time range</p>
      </div>

      <div className="card">
        <h2>Query Parameters</h2>

        <div className="query-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="startTime">Start Time</label>
              <input
                id="startTime"
                type="datetime-local"
                value={startTime}
                onChange={(e) => {
                  setStartTime(e.target.value)
                  setSelectedHour(null)
                }}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="endTime">End Time</label>
              <input
                id="endTime"
                type="datetime-local"
                value={endTime}
                onChange={(e) => {
                  setEndTime(e.target.value)
                  setSelectedHour(null)
                }}
                className="form-input"
              />
            </div>
          </div>

          <div className="hourly-section">
            <div className="hourly-header">
              <label>Hourly Quick Query</label>
              <input
                type="date"
                value={hourlyDate}
                onChange={(e) => {
                  setHourlyDate(e.target.value)
                  setSelectedHour(null)
                }}
                className="form-input hourly-date-input"
              />
            </div>

            <div className="hour-grid">
              {hourlyPresetHours.map((hour) => (
                <button
                  type="button"
                  key={hour}
                  className={`hour-btn${selectedHour === hour ? ' active' : ''}`}
                  onClick={() => handleHourlyPreset(hour)}
                  title={hour === 24 ? '00:00 - 01:00 (next day)' : `${hour.toString().padStart(2, '0')}:00 - ${(hour + 1).toString().padStart(2, '0')}:00`}
                >
                  {hour}
                </button>
              ))}
            </div>

            <p className="hourly-hint">Pick a date and tap an hour to auto-fill the range (24 = midnight of the next day).</p>
          </div>

          <div className="form-group">
            <label htmlFor="query">Query (Chinese or English)</label>
            <input
              id="query"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="form-input"
              placeholder="e.g., 总结这段时间的活动 or Summarize my activities"
            />
          </div>

          <button
            className="btn btn-primary"
            onClick={handleQuery}
            disabled={loading}
          >
            {loading ? 'Querying...' : 'Query Activities'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error">{error}</div>
      )}

      {result && (
        <div className="card">
          <h2>Results</h2>

          <div className="result-summary">
            <div className="result-meta">
              <div className="meta-item">
                <span className="meta-label">Time Range:</span>
                <span className="meta-value">
                  {format(new Date(result.time_range.start), 'PPpp')} - {format(new Date(result.time_range.end), 'PPpp')}
                </span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Activities Found:</span>
                <span className="meta-value">{result.activities_count}</span>
              </div>
            </div>

            <div className="summary-text">
              <h3>Summary</h3>
              <pre>{result.summary}</pre>
            </div>

            {result.activities.length > 0 && (
              <div className="activities-timeline">
                <h3>Timeline</h3>
                {result.activities.map((activity, index) => (
                  <div key={index} className="timeline-item">
                    <div className="timeline-time">
                      {format(new Date(activity.timestamp), 'HH:mm:ss')}
                    </div>
                    <div className="timeline-content">
                      {activity.activity_description}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
