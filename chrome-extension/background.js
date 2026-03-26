// Background script for AI Keyboard RAG Assistant
let selectedText = '';

// Create context menu items
chrome.runtime.onInstalled.addListener(() => {
  // Create parent menu
  chrome.contextMenus.create({
    id: 'ai-keyboard-parent',
    title: 'AI Keyboard Assistant',
    contexts: ['selection']
  });

  // Create submenu items
  chrome.contextMenus.create({
    id: 'fix-grammar',
    parentId: 'ai-keyboard-parent',
    title: '✏️ Fix Grammar',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'rag-reply',
    parentId: 'ai-keyboard-parent',
    title: '🧠 RAG Reply',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'general-reply',
    parentId: 'ai-keyboard-parent',
    title: '💬 General Reply',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'make-professional',
    parentId: 'ai-keyboard-parent',
    title: '👔 Make Professional & Polite',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'describe',
    parentId: 'ai-keyboard-parent',
    title: '📝 Describe',
    contexts: ['selection']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  selectedText = info.selectionText;
  
  try {
    // Inject content script if needed
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['content.js']
    });

    // Send message to content script
    chrome.tabs.sendMessage(tab.id, {
      action: info.menuItemId,
      text: selectedText
    });
  } catch (error) {
    console.error('Error executing script:', error);
  }
});

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getSelectedText') {
    sendResponse({ text: selectedText });
  }
  return true;
});

// API helper functions
async function getSettings() {
  const result = await chrome.storage.sync.get(['baseUrl', 'accessToken', 'refreshToken']);
  return {
    baseUrl: result.baseUrl || 'http://localhost:8000',
    accessToken: result.accessToken || '',
    refreshToken: result.refreshToken || ''
  };
}

async function makeAPIRequest(endpoint, method = 'GET', data = null) {
  const settings = await getSettings();
  const url = `${settings.baseUrl}${endpoint}`;
  
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    }
  };

  if (settings.accessToken) {
    options.headers['Authorization'] = `Bearer ${settings.accessToken}`;
  }

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.message || `HTTP error! status: ${response.status}`;
      } catch {
        errorMessage = `HTTP error! status: ${response.status}`;
      }
      throw new Error(errorMessage);
    }
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { makeAPIRequest, getSettings };
}