/**
 * Popup UI Script for Activity Recorder Extension
 */

// DOM elements
const statusDot = document.getElementById('statusDot');
const statusValue = document.getElementById('statusValue');
const toggleRecordingBtn = document.getElementById('toggleRecording');
const toggleText = document.getElementById('toggleText');
const captureNowBtn = document.getElementById('captureNow');
const intervalInput = document.getElementById('intervalInput');
const saveIntervalBtn = document.getElementById('saveInterval');
const totalActivities = document.getElementById('totalActivities');
const successRate = document.getElementById('successRate');
const lastCapture = document.getElementById('lastCapture');
const connectionStatus = document.getElementById('connectionStatus');
const openDashboardLink = document.getElementById('openDashboard');

// State
let isRecording = false;
let currentInterval = 3;

/**
 * Initialize popup
 */
async function init() {
  console.log('Popup initialized');

  // Load saved interval
  const settings = await chrome.storage.local.get(['interval']);
  if (settings.interval) {
    currentInterval = settings.interval;
    intervalInput.value = currentInterval;
  }

  // Get current status
  await updateStatus();

  // Set up event listeners
  toggleRecordingBtn.addEventListener('click', toggleRecording);
  captureNowBtn.addEventListener('click', captureNow);
  saveIntervalBtn.addEventListener('click', saveInterval);
  openDashboardLink.addEventListener('click', openDashboard);

  // Auto-refresh every 5 seconds
  setInterval(updateStatus, 5000);
}

/**
 * Update status from background
 */
async function updateStatus() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getStatus' });

    if (response.success) {
      const status = response.status;
      isRecording = status.isRecording || status.is_recording || false;

      // Update UI
      updateRecordingUI(isRecording);

      // Update statistics
      if (status.statistics) {
        const stats = status.statistics;
        totalActivities.textContent = stats.total_activities || 0;

        const rate = stats.success_rate || 0;
        successRate.textContent = `${rate}%`;

        if (stats.last_activity) {
          lastCapture.textContent = formatTimestamp(stats.last_activity);
        }
      }

      // Update last capture time
      if (status.lastCapture) {
        lastCapture.textContent = formatTimestamp(status.lastCapture);
      }

      // Hide connection error
      connectionStatus.style.display = 'none';

    } else {
      console.error('Failed to get status:', response.error);
      showConnectionError();
    }

  } catch (error) {
    console.error('Error updating status:', error);
    showConnectionError();
  }
}

/**
 * Toggle recording on/off
 */
async function toggleRecording() {
  toggleRecordingBtn.disabled = true;

  try {
    const action = isRecording ? 'stopRecording' : 'startRecording';
    const response = await chrome.runtime.sendMessage({ action });

    if (response.success) {
      isRecording = !isRecording;
      updateRecordingUI(isRecording);

      // Show notification
      showNotification(
        isRecording ? 'Recording started' : 'Recording stopped',
        isRecording ? 'Screenshots will be captured automatically' : 'Automatic capture stopped'
      );

    } else {
      console.error('Failed to toggle recording:', response.error);
      showNotification('Error', response.error || 'Failed to toggle recording');
    }

  } catch (error) {
    console.error('Error toggling recording:', error);
    showNotification('Error', error.message);
  } finally {
    toggleRecordingBtn.disabled = false;
  }
}

/**
 * Capture screenshot now
 */
async function captureNow() {
  captureNowBtn.disabled = true;
  captureNowBtn.innerHTML = '<span>Capturing...</span>';

  try {
    const response = await chrome.runtime.sendMessage({ action: 'captureNow' });

    if (response.success) {
      showNotification('Capture successful', 'Screenshot captured and analyzed');
      await updateStatus();
    } else {
      console.error('Failed to capture:', response.error);
      showNotification('Capture failed', response.error || 'Could not capture screenshot');
    }

  } catch (error) {
    console.error('Error capturing:', error);
    showNotification('Error', error.message);
  } finally {
    captureNowBtn.disabled = false;
    captureNowBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
        <circle cx="8" cy="8" r="2" fill="currentColor"/>
      </svg>
      Capture Now
    `;
  }
}

/**
 * Save interval setting
 */
async function saveInterval() {
  const interval = parseInt(intervalInput.value);

  if (interval < 1 || interval > 60) {
    showNotification('Invalid interval', 'Please enter a value between 1 and 60 minutes');
    return;
  }

  try {
    const response = await chrome.runtime.sendMessage({
      action: 'updateSettings',
      settings: { interval: interval * 60 } // Convert to seconds
    });

    if (response.success) {
      currentInterval = interval;
      showNotification('Settings saved', `Interval updated to ${interval} minute(s)`);
    } else {
      showNotification('Error', response.error || 'Failed to save settings');
    }

  } catch (error) {
    console.error('Error saving interval:', error);
    showNotification('Error', error.message);
  }
}

/**
 * Open web dashboard
 */
function openDashboard(e) {
  e.preventDefault();
  // TODO: Update this URL when dashboard is deployed
  chrome.tabs.create({ url: 'http://localhost:3000' });
}

/**
 * Update recording UI state
 */
function updateRecordingUI(recording) {
  if (recording) {
    statusDot.classList.add('recording');
    statusValue.textContent = 'Recording';
    toggleRecordingBtn.classList.add('recording');
    toggleText.textContent = 'Stop Recording';
    toggleRecordingBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="4" width="8" height="8" fill="currentColor"/>
      </svg>
      <span>Stop Recording</span>
    `;
  } else {
    statusDot.classList.remove('recording');
    statusValue.textContent = 'Stopped';
    toggleRecordingBtn.classList.remove('recording');
    toggleText.textContent = 'Start Recording';
    toggleRecordingBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="8" cy="8" r="6" fill="currentColor"/>
      </svg>
      <span>Start Recording</span>
    `;
  }
}

/**
 * Show connection error
 */
function showConnectionError() {
  connectionStatus.style.display = 'flex';
  statusValue.textContent = 'Not Connected';
  toggleRecordingBtn.disabled = true;
  captureNowBtn.disabled = true;
}

/**
 * Show notification (simple toast)
 */
function showNotification(title, message) {
  // For now, just log to console
  // In a real implementation, you might want to use Chrome notifications API
  // or a toast library
  console.log(`${title}: ${message}`);
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) {
    return 'Just now';
  } else if (diffMins < 60) {
    return `${diffMins} min ago`;
  } else if (diffMins < 1440) {
    const hours = Math.floor(diffMins / 60);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else {
    return date.toLocaleString();
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
