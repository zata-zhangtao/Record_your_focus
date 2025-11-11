/**
 * Background Service Worker for Activity Recorder Extension
 *
 * This service worker:
 * - Manages connection to native messaging host
 * - Schedules periodic screenshot captures
 * - Handles recording state
 * - Provides API for popup and options pages
 */

const NATIVE_HOST_NAME = 'com.activity_recorder.host';
const DEFAULT_INTERVAL = 180; // 3 minutes in seconds

// Recording state
let recordingState = {
  isRecording: false,
  interval: DEFAULT_INTERVAL,
  lastCapture: null,
  statistics: {
    total_activities: 0,
    successful_analyses: 0,
    failed_analyses: 0
  }
};

/**
 * Initialize extension
 */
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('Extension installed/updated:', details.reason);

  // Load saved settings
  const settings = await chrome.storage.local.get(['interval', 'autoStart']);

  if (settings.interval) {
    recordingState.interval = settings.interval;
  }

  // Auto-start if enabled
  if (settings.autoStart && details.reason === 'install') {
    startRecording();
  }

  // Set default badge
  updateBadge();
});

/**
 * Send message to native host
 */
async function sendNativeMessage(message) {
  return new Promise((resolve, reject) => {
    try {
      const port = chrome.runtime.connectNative(NATIVE_HOST_NAME);

      // Set up response handler
      port.onMessage.addListener((response) => {
        console.log('Native host response:', response);
        port.disconnect();
        resolve(response);
      });

      // Set up error handler
      port.onDisconnect.addListener(() => {
        const error = chrome.runtime.lastError;
        if (error) {
          console.error('Native host error:', error);
          reject(new Error(error.message));
        }
      });

      // Send message
      console.log('Sending to native host:', message);
      port.postMessage(message);

    } catch (error) {
      console.error('Failed to connect to native host:', error);
      reject(error);
    }
  });
}

/**
 * Start recording
 */
async function startRecording() {
  if (recordingState.isRecording) {
    console.log('Recording already running');
    return { success: false, error: 'Recording already running' };
  }

  try {
    // Send start command to native host
    const response = await sendNativeMessage({
      command: 'start_recording',
      interval: recordingState.interval
    });

    if (response.success) {
      recordingState.isRecording = true;

      // Set up periodic alarm for UI updates
      chrome.alarms.create('updateStats', { periodInMinutes: 1 });

      // Update badge
      updateBadge();

      console.log('Recording started');
      return { success: true };
    } else {
      throw new Error(response.error || 'Failed to start recording');
    }

  } catch (error) {
    console.error('Failed to start recording:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Stop recording
 */
async function stopRecording() {
  if (!recordingState.isRecording) {
    console.log('Recording not running');
    return { success: false, error: 'Recording not running' };
  }

  try {
    // Send stop command to native host
    const response = await sendNativeMessage({
      command: 'stop_recording'
    });

    if (response.success) {
      recordingState.isRecording = false;

      // Clear alarms
      chrome.alarms.clear('updateStats');

      // Update badge
      updateBadge();

      console.log('Recording stopped');
      return { success: true };
    } else {
      throw new Error(response.error || 'Failed to stop recording');
    }

  } catch (error) {
    console.error('Failed to stop recording:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Capture now (manual trigger)
 */
async function captureNow() {
  try {
    const response = await sendNativeMessage({
      command: 'capture_now'
    });

    if (response.success) {
      recordingState.lastCapture = new Date().toISOString();
      await updateStatistics();
      return { success: true, activity: response.activity };
    } else {
      throw new Error(response.error || 'Capture failed');
    }

  } catch (error) {
    console.error('Failed to capture:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get activities from native host
 */
async function getActivities(limit = 10, date = null) {
  try {
    const response = await sendNativeMessage({
      command: 'get_activities',
      limit: limit,
      date: date
    });

    if (response.success) {
      return { success: true, activities: response.activities };
    } else {
      throw new Error(response.error || 'Failed to get activities');
    }

  } catch (error) {
    console.error('Failed to get activities:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Update statistics from native host
 */
async function updateStatistics() {
  try {
    const response = await sendNativeMessage({
      command: 'get_statistics'
    });

    if (response.success) {
      recordingState.statistics = response.statistics;
      return { success: true, statistics: response.statistics };
    }

  } catch (error) {
    console.error('Failed to get statistics:', error);
    return { success: false };
  }
}

/**
 * Update settings
 */
async function updateSettings(settings) {
  try {
    // Update local state
    if (settings.interval) {
      recordingState.interval = settings.interval;
    }

    // Save to storage
    await chrome.storage.local.set(settings);

    // Send to native host
    const response = await sendNativeMessage({
      command: 'update_settings',
      settings: settings
    });

    return response;

  } catch (error) {
    console.error('Failed to update settings:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get current status
 */
async function getStatus() {
  try {
    const response = await sendNativeMessage({
      command: 'get_status'
    });

    if (response.success) {
      // Sync state with native host
      recordingState.isRecording = response.status.is_recording;
      recordingState.statistics = response.status.statistics;

      return {
        success: true,
        status: {
          ...recordingState,
          ...response.status
        }
      };
    }

    // Fallback to local state
    return { success: true, status: recordingState };

  } catch (error) {
    console.error('Failed to get status:', error);
    // Return local state as fallback
    return { success: true, status: recordingState };
  }
}

/**
 * Update extension badge
 */
function updateBadge() {
  if (recordingState.isRecording) {
    chrome.action.setBadgeText({ text: 'ON' });
    chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });
  } else {
    chrome.action.setBadgeText({ text: '' });
  }
}

/**
 * Handle alarms
 */
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'updateStats') {
    updateStatistics();
  }
});

/**
 * Handle messages from popup/options pages
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Received message:', request);

  switch (request.action) {
    case 'startRecording':
      startRecording().then(sendResponse);
      return true;

    case 'stopRecording':
      stopRecording().then(sendResponse);
      return true;

    case 'captureNow':
      captureNow().then(sendResponse);
      return true;

    case 'getStatus':
      getStatus().then(sendResponse);
      return true;

    case 'getActivities':
      getActivities(request.limit, request.date).then(sendResponse);
      return true;

    case 'updateSettings':
      updateSettings(request.settings).then(sendResponse);
      return true;

    case 'getStatistics':
      updateStatistics().then(sendResponse);
      return true;

    default:
      sendResponse({ success: false, error: 'Unknown action' });
      return false;
  }
});

// Log that service worker is ready
console.log('Activity Recorder service worker loaded');
