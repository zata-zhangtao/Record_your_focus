export default function Settings() {
  return (
    <div className="page settings-page">
      <div className="page-header">
        <h1>Settings</h1>
        <p>Configure your activity recorder settings</p>
      </div>

      <div className="card">
        <h2>Extension Settings</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '8px' }}>
          Settings are managed through the browser extension.
          Click the extension icon in your browser toolbar and select "Settings" to configure:
        </p>

        <ul style={{ marginTop: '16px', marginLeft: '20px', fontSize: '14px' }}>
          <li>Capture interval</li>
          <li>Auto-start recording</li>
          <li>DashScope API key</li>
          <li>AI model selection</li>
          <li>Data retention policies</li>
        </ul>
      </div>

      <div className="card">
        <h2>About This Dashboard</h2>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          <p style={{ marginBottom: '12px' }}>
            This web dashboard provides a visual interface to view and analyze your recorded activities.
          </p>

          <p style={{ marginBottom: '12px' }}>
            <strong>Data Source:</strong> The dashboard reads from <code>activity_log.json</code> which is
            updated by the native host application when activities are recorded.
          </p>

          <p>
            <strong>Privacy:</strong> All data is stored locally on your computer. No information is sent
            to external servers except for AI analysis via your DashScope API key.
          </p>
        </div>
      </div>

      <div className="card">
        <h2>Quick Links</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
          <a
            href="https://dashscope.console.aliyun.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="link-button"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 3v14m0-14l4 4m-4-4L6 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            DashScope Console (Get API Key)
          </a>

          <a
            href="https://help.aliyun.com/zh/dashscope/"
            target="_blank"
            rel="noopener noreferrer"
            className="link-button"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M9 5h2M9 9h6m-6 4h6M5 5h.01M5 9h.01M5 13h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            DashScope Documentation
          </a>

          <a
            href="chrome://extensions"
            className="link-button"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M10 7v3M10 13h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Browser Extensions Page
          </a>
        </div>
      </div>
    </div>
  )
}
