/**
 * Options page script for Activity Recorder Extension
 */

// DOM elements
const captureIntervalInput = document.getElementById('captureInterval');
const autoStartCheckbox = document.getElementById('autoStart');
const apiKeyInput = document.getElementById('apiKey');
const toggleApiKeyBtn = document.getElementById('toggleApiKey');
const modelNameSelect = document.getElementById('modelName');
const thinkingModeCheckbox = document.getElementById('thinkingMode');
const retentionDaysInput = document.getElementById('retentionDays');
const maxScreenshotsInput = document.getElementById('maxScreenshots');
const saveSettingsBtn = document.getElementById('saveSettings');
const resetSettingsBtn = document.getElementById('resetSettings');
const exportDataBtn = document.getElementById('exportData');
const saveStatus = document.getElementById('saveStatus');
const nativeHostStatus = document.getElementById('nativeHostStatus');

// Default settings
const DEFAULT_SETTINGS = {
  interval: 180, // 3 minutes in seconds
  autoStart: false,
  apiKey: '',
  modelName: 'qwen3-vl-plus',
  thinkingMode: true,
  retentionDays: 30,
  maxScreenshots: 50
};

/**
 * Initialize options page
 */
async function init() {
  console.log('Options page initialized');

  // Load settings
  await loadSettings();

  // Check native host connection
  await checkNativeHost();

  // Set up event listeners
  saveSettingsBtn.addEventListener('click', saveSettings);
  resetSettingsBtn.addEventListener('click', resetSettings);
  exportDataBtn.addEventListener('click', exportData);
  toggleApiKeyBtn.addEventListener('click', toggleApiKeyVisibility);
}

/**
 * Load settings from storage
 */
async function loadSettings() {
  try {
    const settings = await chrome.storage.local.get(DEFAULT_SETTINGS);

    // Populate form
    captureIntervalInput.value = Math.floor(settings.interval / 60); // Convert seconds to minutes
    autoStartCheckbox.checked = settings.autoStart;
    apiKeyInput.value = settings.apiKey || '';
    modelNameSelect.value = settings.modelName;
    thinkingModeCheckbox.checked = settings.thinkingMode;
    retentionDaysInput.value = settings.retentionDays;
    maxScreenshotsInput.value = settings.maxScreenshots;

    console.log('Settings loaded:', settings);

  } catch (error) {
    console.error('Failed to load settings:', error);
    showStatus('Failed to load settings', 'error');
  }
}

/**
 * Save settings to storage and native host
 */
async function saveSettings() {
  try {
    // Validate inputs
    const interval = parseInt(captureIntervalInput.value);
    if (interval < 1 || interval > 60) {
      showStatus('Interval must be between 1 and 60 minutes', 'error');
      return;
    }

    const retentionDays = parseInt(retentionDaysInput.value);
    if (retentionDays < 1 || retentionDays > 365) {
      showStatus('Retention must be between 1 and 365 days', 'error');
      return;
    }

    const maxScreenshots = parseInt(maxScreenshotsInput.value);
    if (maxScreenshots < 10 || maxScreenshots > 500) {
      showStatus('Max screenshots must be between 10 and 500', 'error');
      return;
    }

    // Collect settings
    const settings = {
      interval: interval * 60, // Convert to seconds
      autoStart: autoStartCheckbox.checked,
      apiKey: apiKeyInput.value,
      modelName: modelNameSelect.value,
      thinkingMode: thinkingModeCheckbox.checked,
      retentionDays: retentionDays,
      maxScreenshots: maxScreenshots
    };

    // Save to storage
    await chrome.storage.local.set(settings);

    // Send to background/native host
    const response = await chrome.runtime.sendMessage({
      action: 'updateSettings',
      settings: {
        interval: settings.interval,
        api_key: settings.apiKey,
        model_name: settings.modelName
      }
    });

    if (response && response.success) {
      showStatus('Settings saved successfully', 'success');
    } else {
      showStatus('Settings saved (native host not connected)', 'warning');
    }

    console.log('Settings saved:', settings);

  } catch (error) {
    console.error('Failed to save settings:', error);
    showStatus('Failed to save settings: ' + error.message, 'error');
  }
}

/**
 * Reset settings to defaults
 */
async function resetSettings() {
  if (!confirm('Are you sure you want to reset all settings to defaults?')) {
    return;
  }

  try {
    await chrome.storage.local.set(DEFAULT_SETTINGS);
    await loadSettings();
    showStatus('Settings reset to defaults', 'success');

  } catch (error) {
    console.error('Failed to reset settings:', error);
    showStatus('Failed to reset settings', 'error');
  }
}

/**
 * Export activity data
 */
async function exportData() {
  try {
    exportDataBtn.disabled = true;
    exportDataBtn.innerHTML = '<span>Exporting...</span>';

    const response = await chrome.runtime.sendMessage({
      action: 'getActivities',
      limit: 1000 // Get many activities
    });

    if (response && response.success) {
      const activities = response.activities;

      // Create export data
      const exportData = {
        exported_at: new Date().toISOString(),
        total_activities: activities.length,
        activities: activities
      };

      // Download as JSON
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `activity_export_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showStatus(`Exported ${activities.length} activities`, 'success');

    } else {
      throw new Error(response?.error || 'Failed to get activities');
    }

  } catch (error) {
    console.error('Failed to export data:', error);
    showStatus('Failed to export data: ' + error.message, 'error');
  } finally {
    exportDataBtn.disabled = false;
    exportDataBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 2v8m0 0L5 7m3 3l3-3M3 12v1a1 1 0 001 1h8a1 1 0 001-1v-1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      Export
    `;
  }
}

/**
 * Toggle API key visibility
 */
function toggleApiKeyVisibility() {
  if (apiKeyInput.type === 'password') {
    apiKeyInput.type = 'text';
  } else {
    apiKeyInput.type = 'password';
  }
}

/**
 * Check native host connection
 */
async function checkNativeHost() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getStatus' });

    if (response && response.success) {
      nativeHostStatus.textContent = 'Connected';
      nativeHostStatus.style.color = 'var(--primary-color)';
    } else {
      nativeHostStatus.textContent = 'Not Connected';
      nativeHostStatus.style.color = 'var(--text-secondary)';
    }

  } catch (error) {
    nativeHostStatus.textContent = 'Error';
    nativeHostStatus.style.color = '#f44336';
  }
}

/**
 * Show status message
 */
function showStatus(message, type = 'info') {
  saveStatus.textContent = message;

  switch (type) {
    case 'success':
      saveStatus.style.color = 'var(--primary-color)';
      break;
    case 'error':
      saveStatus.style.color = '#f44336';
      break;
    case 'warning':
      saveStatus.style.color = '#ff9800';
      break;
    default:
      saveStatus.style.color = 'var(--text-secondary)';
  }

  // Clear after 5 seconds
  setTimeout(() => {
    saveStatus.textContent = '';
  }, 5000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
