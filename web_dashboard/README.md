# Activity Recorder - Web Dashboard

A modern React-based web dashboard for viewing and analyzing your activity records.

## Features

- 📊 **Dashboard Overview**: View statistics and recent activities at a glance
- 📝 **Activity Timeline**: Browse all recorded activities with search and filters
- ⏰ **Time Query**: Analyze activities within specific time ranges
- 🎨 **Modern UI**: Clean, responsive design built with React

## Prerequisites

- Node.js 18+ and npm
- Activity Recorder native host and browser extension installed
- Activity data in `activity_log.json`

## Installation

```bash
cd web_dashboard
npm install
```

## Development

```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## Production Build

```bash
npm run build
```

The optimized build will be in the `dist/` directory. You can serve it with any static file server:

```bash
npm run preview  # Preview production build locally
```

## Project Structure

```
web_dashboard/
├── src/
│   ├── components/
│   │   ├── Layout.jsx          # Main layout with navigation
│   │   └── Layout.css
│   ├── pages/
│   │   ├── Dashboard.jsx       # Dashboard overview
│   │   ├── Dashboard.css
│   │   ├── Activities.jsx      # Activity list and search
│   │   ├── Activities.css
│   │   ├── TimeQuery.jsx       # Time range analysis
│   │   ├── TimeQuery.css
│   │   ├── Settings.jsx        # Settings and links
│   │   └── Settings.css
│   ├── App.jsx                 # Main app component
│   ├── App.css
│   ├── main.jsx               # React entry point
│   └── index.css              # Global styles
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## Pages

### Dashboard (`/dashboard`)

- **Statistics Cards**: Total activities, success rate, failed analyses
- **Recent Activities**: Last 5 recorded activities
- **Quick Actions**: Links to other pages

### Activities (`/activities`)

- **Activity Grid**: All activities in card layout
- **Search**: Filter activities by description
- **Date Filter**: View activities from specific dates
- **Screenshot Preview**: View screenshots (if available)

### Time Query (`/time-query`)

- **Date Range Selector**: Choose start and end time
- **Custom Query**: Ask questions about activities in the time range
- **Timeline View**: See chronological list of activities
- **Summary**: AI-generated summary (when connected to backend)

### Settings (`/settings`)

- **Extension Settings**: Link to browser extension settings
- **Quick Links**: DashScope console, documentation
- **About Information**: Dashboard version and privacy info

## Data Source

The dashboard reads activity data from `/activity_log.json`, which is created and updated by the native host application. Make sure the dashboard can access this file.

### Development Setup

For development, you can:

1. **Copy the file**: Copy `activity_log.json` to the `public/` directory
   ```bash
   cp ../activity_log.json public/
   ```

2. **Symlink**: Create a symlink (Linux/macOS)
   ```bash
   cd public && ln -s ../../activity_log.json .
   ```

3. **Backend Proxy**: Configure Vite to proxy requests to a backend server (already configured in `vite.config.js`)

## Deployment

### Option 1: Serve Locally

Run alongside the native host application:

```bash
npm run dev  # Development
# or
npm run build && npm run preview  # Production
```

### Option 2: Static Hosting

Build and deploy to static hosting services:

- **GitHub Pages**: Deploy `dist/` folder
- **Netlify**: Connect repository, auto-deploy on push
- **Vercel**: Same as Netlify
- **Your own server**: Serve `dist/` with nginx, Apache, etc.

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name activity-recorder.local;
    root /path/to/web_dashboard/dist;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /activity_log.json {
        alias /path/to/auto_record_my_activates/activity_log.json;
    }

    location /screenshots/ {
        alias /path/to/auto_record_my_activates/screenshots/;
    }
}
```

### Option 3: Electron App

Package as a desktop app with Electron for easier local usage:

```bash
npm install --save-dev electron electron-builder
```

Create `electron/main.js`:

```javascript
const { app, BrowserWindow } = require('electron')
const path = require('path')

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  win.loadFile(path.join(__dirname, '../dist/index.html'))
}

app.whenReady().then(createWindow)
```

## Customization

### Colors

Edit color variables in `src/index.css`:

```css
:root {
  --primary-color: #4CAF50;  /* Change primary color */
  --secondary-color: #2196F3;
  /* ... other colors */
}
```

### Layout

- Adjust sidebar width in `src/components/Layout.css`
- Change max-width for content areas in page CSS files
- Modify grid columns in Activities page

### Features

To add new features:

1. Create new page component in `src/pages/`
2. Add route in `src/App.jsx`
3. Add navigation link in `src/components/Layout.jsx`

## Browser Compatibility

Tested on:
- Chrome/Chromium 90+
- Firefox 88+
- Edge 90+
- Safari 14+

## Troubleshooting

### Activities not showing

- Verify `activity_log.json` exists in the project root
- Check browser console for fetch errors
- Ensure native host has created activity records

### Screenshots not loading

- Verify screenshot files exist in `screenshots/` directory
- Check that file paths in `activity_log.json` are correct
- Configure server to serve the screenshots directory

### Build errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

## License

[Your License Here]

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Related

- **Browser Extension**: `../browser_extension/chrome/`
- **Native Host**: `../native_host.py`
- **Main Project**: `../README.md`
