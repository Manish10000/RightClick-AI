// Content script for AI Keyboard RAG Assistant
let isProcessing = false;

// Simple Markdown to HTML converter
function markdownToHtml(markdown) {
  let html = markdown;
  
  // Headers (less common now with improved prompts)
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  
  // Bold text (less common now)
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Italic text (less common now)
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Code blocks (less common now)
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  
  // Inline code (less common now)
  html = html.replace(/`(.*?)`/g, '<code>$1</code>');
  
  // Simple bullet points (more common now)
  html = html.replace(/^• (.*$)/gim, '<li>$1</li>');
  html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
  
  // Wrap consecutive list items in ul tags
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  
  // Line breaks - convert double line breaks to paragraphs
  html = html.replace(/\n\n/g, '</p><p>');
  html = '<p>' + html + '</p>';
  
  // Clean up empty paragraphs and fix list formatting
  html = html.replace(/<p><\/p>/g, '');
  html = html.replace(/<p>(<h[1-6]>)/g, '$1');
  html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1');
  html = html.replace(/<p>(<ul>)/g, '$1');
  html = html.replace(/(<\/ul>)<\/p>/g, '$1');
  html = html.replace(/<p>(<pre>)/g, '$1');
  html = html.replace(/(<\/pre>)<\/p>/g, '$1');
  
  return html;
}

// Create floating result window
function createResultWindow(content, position) {
  console.log('🪟 Creating result window with content:', content.substring(0, 100) + '...');
  console.log('📍 Position:', position);
  console.log('📝 Full content length:', content.length);
  console.log('📝 Content preview:', JSON.stringify(content.substring(0, 200)));
  
  // Remove existing window
  const existing = document.getElementById('ai-keyboard-result');
  if (existing) {
    existing.remove();
    console.log('🗑️ Removed existing result window');
  }

  // Create backdrop for click-outside-to-close
  const backdrop = document.createElement('div');
  backdrop.id = 'ai-keyboard-backdrop';
  backdrop.style.cssText = `
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    background: rgba(0, 0, 0, 0.1) !important;
    z-index: 2147483646 !important;
    display: block !important;
    visibility: visible !important;
  `;

  const resultWindow = document.createElement('div');
  resultWindow.id = 'ai-keyboard-result';
  resultWindow.className = 'ai-keyboard-window';
  
  // Escape content for HTML
  const escapedContent = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
  
  // Convert markdown to HTML
  const htmlContent = markdownToHtml(content);
  
  resultWindow.innerHTML = `
    <div class="ai-keyboard-header">
      <span class="ai-keyboard-title">AI Assistant Result</span>
      <button class="ai-keyboard-close">×</button>
    </div>
    <div class="ai-keyboard-content">
      <div class="ai-keyboard-result-text" style="
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-radius: 4px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        line-height: 1.6 !important;
        color: #333 !important;
        font-size: 14px !important;
        font-family: Arial, sans-serif !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        max-height: 400px !important;
        overflow-y: auto !important;
        user-select: text !important;
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
        -ms-user-select: text !important;
        cursor: text !important;
      ">${htmlContent}</div>
      <div class="ai-keyboard-actions">
        <button class="ai-keyboard-btn ai-keyboard-copy">Copy</button>
        <button class="ai-keyboard-btn ai-keyboard-replace">Replace</button>
      </div>
    </div>
  `;

  // Position the window (ensure it's visible on screen)
  const x = Math.max(10, Math.min(position.x, window.innerWidth - 520));
  const y = Math.max(10, Math.min(position.y, window.innerHeight - 300));
  
  resultWindow.style.cssText = `
    position: fixed !important;
    left: ${x}px !important;
    top: ${y}px !important;
    z-index: 2147483647 !important;
    display: block !important;
    visibility: visible !important;
    background: white !important;
    border: 2px solid #4CAF50 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    min-width: 300px !important;
    max-width: 500px !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    font-size: 14px !important;
    opacity: 1 !important;
    transform: scale(1) !important;
    pointer-events: auto !important;
  `;

  // Add backdrop first, then window
  document.body.appendChild(backdrop);
  document.body.appendChild(resultWindow);
  
  console.log('✅ Result window added to DOM at position:', x, y);
  console.log('📝 Rendered HTML content preview:', htmlContent.substring(0, 200) + '...');
  
  // Close function
  function closeWindow() {
    if (backdrop.parentNode) backdrop.remove();
    if (resultWindow.parentNode) resultWindow.remove();
    document.removeEventListener('keydown', handleKeyDown);
    console.log('🗑️ Result window closed');
  }
  
  // Handle ESC key
  function handleKeyDown(e) {
    if (e.key === 'Escape') {
      closeWindow();
    }
  }
  
  // Add event listeners
  const closeBtn = resultWindow.querySelector('.ai-keyboard-close');
  closeBtn.addEventListener('click', closeWindow);
  
  // Click outside to close
  backdrop.addEventListener('click', closeWindow);
  
  // ESC key to close
  document.addEventListener('keydown', handleKeyDown);
  
  const copyBtn = resultWindow.querySelector('.ai-keyboard-copy');
  copyBtn.addEventListener('click', () => {
    copyToClipboard(content);
  });
  
  const replaceBtn = resultWindow.querySelector('.ai-keyboard-replace');
  replaceBtn.addEventListener('click', () => {
    replaceSelectedText(content);
    closeWindow();
  });
  
  // Make draggable
  makeDraggable(resultWindow);
  
  // Force visibility with a slight delay
  setTimeout(() => {
    resultWindow.style.opacity = '1';
    resultWindow.style.transform = 'scale(1)';
    console.log('🎉 Result window fully initialized and visible');
  }, 10);
  
  return resultWindow;
}

// Create loading indicator with spinner cursor
function showLoading(position) {
  const existing = document.getElementById('ai-keyboard-loading');
  if (existing) {
    existing.remove();
  }

  // Change cursor to loading spinner
  document.body.style.cursor = 'wait';

  const loading = document.createElement('div');
  loading.id = 'ai-keyboard-loading';
  loading.className = 'ai-keyboard-loading';
  loading.innerHTML = `
    <div class="ai-keyboard-spinner"></div>
    <div>Processing...</div>
  `;
  
  loading.style.left = `${position.x}px`;
  loading.style.top = `${position.y}px`;
  
  document.body.appendChild(loading);
}

function hideLoading() {
  // Reset cursor
  document.body.style.cursor = 'default';
  
  const loading = document.getElementById('ai-keyboard-loading');
  if (loading) {
    loading.remove();
  }
}

// Make element draggable
function makeDraggable(element) {
  let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  const header = element.querySelector('.ai-keyboard-header');
  
  header.onmousedown = dragMouseDown;

  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    element.style.top = (element.offsetTop - pos2) + "px";
    element.style.left = (element.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    document.onmouseup = null;
    document.onmousemove = null;
  }
}

// Copy to clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showNotification('Copied to clipboard!');
  }).catch(err => {
    console.error('Failed to copy:', err);
    showNotification('Failed to copy to clipboard', 'error');
  });
}

// Replace selected text
function replaceSelectedText(newText) {
  const selection = window.getSelection();
  if (selection.rangeCount > 0) {
    const range = selection.getRangeAt(0);
    range.deleteContents();
    range.insertNode(document.createTextNode(newText));
    selection.removeAllRanges();
    showNotification('Text replaced!');
  }
}

// Show notification
function showNotification(message, type = 'success') {
  // Remove existing notifications
  const existingNotifications = document.querySelectorAll('.ai-keyboard-notification');
  existingNotifications.forEach(notification => notification.remove());
  
  const notification = document.createElement('div');
  notification.className = `ai-keyboard-notification ai-keyboard-${type}`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Auto-remove after 4 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 4000);
}

// Get settings from storage
async function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(['baseUrl', 'accessToken', 'refreshToken'], (result) => {
      resolve({
        baseUrl: result.baseUrl || 'http://localhost:8000',
        accessToken: result.accessToken || '',
        refreshToken: result.refreshToken || ''
      });
    });
  });
}

// Make API request
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
}

// Process text based on action
async function processText(action, text, position) {
  if (isProcessing) return;
  
  isProcessing = true;
  
  // Store the current selection range BEFORE showing loading
  let storedRange = null;
  const selection = window.getSelection();
  if (selection.rangeCount > 0) {
    storedRange = selection.getRangeAt(0).cloneRange();
    console.log('📌 Stored selection range:', storedRange.toString());
  }
  
  showLoading(position);

  try {
    let prompt = '';
    let useRAG = false;
    let autoReplace = false;
    let showPopup = false;

    switch (action) {
      case 'fix-grammar':
        prompt = `You are a grammar and spelling correction expert. Fix all grammar, spelling, and punctuation errors in the following text. Return ONLY the corrected text without quotes, explanations, or additional formatting.

Text to fix: "${text}"

Corrected text:`;
        useRAG = false;
        autoReplace = true;
        break;
      case 'rag-reply':
        prompt = `Please provide a comprehensive reply to the following text using relevant information from the knowledge base: "${text}"`;
        useRAG = true;
        autoReplace = true;
        break;
      case 'general-reply':
        prompt = `You are a helpful AI assistant. Provide a thoughtful and appropriate reply to the following text. Be concise and helpful.

Text: "${text}"

Your reply:`;
        useRAG = false;
        autoReplace = true;
        break;
      case 'make-professional':
        prompt = `You are a professional writing expert. Rewrite the following text to be more professional, polite, and formal while maintaining the original meaning. Return ONLY the rewritten text with no explanations, no quotes, no additional text.

Text to rewrite: "${text}"

Professional version:`;
        useRAG = false;
        autoReplace = true;
        break;
      case 'describe':
        prompt = `You are an expert at explaining and describing text. Provide a detailed explanation of the following text, including its meaning, context, and any relevant information.

Text to describe: "${text}"

Description:`;
        useRAG = false;
        autoReplace = false;
        showPopup = true;
        break;
      default:
        throw new Error('Unknown action');
    }

    console.log('Processing action:', action, 'Text:', text.substring(0, 50) + '...', 'UseRAG:', useRAG);

    // Use appropriate endpoint based on RAG requirement
    const endpoint = useRAG ? '/chat' : '/chat/direct';
    
    // Prepare request data based on endpoint
    const requestData = {
      message: prompt,
      model: 'llama3.1:8b'
    };
    
    // Only add context_chunks for RAG endpoint
    if (useRAG) {
      requestData.context_chunks = 5;
    }
    
    console.log('🚀 Using endpoint:', endpoint);
    console.log('📤 Request data:', requestData);
    
    const response = await makeAPIRequest(endpoint, 'POST', requestData);

    hideLoading();
    
    const aiResponse = response.response.trim();
    
    // Clean up the response by removing surrounding quotes
    let cleanedResponse = aiResponse;
    if ((cleanedResponse.startsWith('"') && cleanedResponse.endsWith('"')) ||
        (cleanedResponse.startsWith("'") && cleanedResponse.endsWith("'"))) {
      cleanedResponse = cleanedResponse.slice(1, -1);
    }
    
    console.log('📥 AI Response:', cleanedResponse.substring(0, 100) + '...');
    console.log('🔍 Used RAG:', response.used_rag, 'Sources:', response.num_sources);

    if (showPopup) {
      // Show popup window for describe action
      console.log('🪟 Creating result window for describe action');
      console.log('📝 Content to show:', cleanedResponse);
      console.log('📍 Position for popup:', position);
      
      // Ensure we have valid position
      const safePosition = {
        x: position.x || 100,
        y: position.y || 100
      };
      
      const resultWindow = createResultWindow(cleanedResponse, safePosition);
      
      // Double-check if window was created and is visible
      setTimeout(() => {
        const windowInDOM = document.getElementById('ai-keyboard-result');
        if (windowInDOM) {
          console.log('✅ Result window confirmed in DOM');
          console.log('📊 Window styles:', {
            display: windowInDOM.style.display,
            visibility: windowInDOM.style.visibility,
            zIndex: windowInDOM.style.zIndex,
            position: windowInDOM.style.position
          });
        } else {
          console.error('❌ Result window not found in DOM!');
        }
      }, 100);
    } else if (autoReplace) {
      // Auto-replace and copy to clipboard
      let replacementSuccess = false;
      
      // Copy to clipboard first
      try {
        await navigator.clipboard.writeText(cleanedResponse);
        console.log('✅ Copied to clipboard');
      } catch (clipboardError) {
        console.warn('❌ Failed to copy to clipboard:', clipboardError);
      }
      
      // Try to replace selected text using stored range
      try {
        if (storedRange) {
          console.log('🔄 Attempting text replacement...');
          console.log('📝 Original text:', storedRange.toString());
          console.log('🆕 New text:', cleanedResponse);
          
          // Create a new range from the stored range
          const newRange = storedRange.cloneRange();
          
          // Delete the original content
          newRange.deleteContents();
          
          // Insert the new text
          const textNode = document.createTextNode(cleanedResponse);
          newRange.insertNode(textNode);
          
          // Clear selection
          selection.removeAllRanges();
          
          replacementSuccess = true;
          console.log('✅ Text replaced successfully');
          showNotification('✅ Text fixed and copied to clipboard!');
        } else {
          console.log('❌ No stored range available');
          showNotification('📋 Result copied to clipboard (no selection stored)');
        }
      } catch (replaceError) {
        console.error('❌ Text replacement failed:', replaceError);
        showNotification('📋 Result copied to clipboard (replacement failed)');
      }
      
      // If replacement failed, show the result in a popup as backup
      if (!replacementSuccess) {
        console.log('🪟 Showing backup result window');
        setTimeout(() => {
          createResultWindow(cleanedResponse, position);
        }, 1000);
      }
    }

  } catch (error) {
    hideLoading();
    console.error('❌ Error processing text:', error);
    showNotification('❌ Error: ' + error.message, 'error');
  } finally {
    isProcessing = false;
  }
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('📨 Received message:', request);
  
  if (request.action && request.text) {
    const selection = window.getSelection();
    let position = { x: 100, y: 100 }; // Default position
    
    try {
      if (selection.rangeCount > 0) {
        const rect = selection.getRangeAt(0).getBoundingClientRect();
        position = {
          x: rect.left + window.scrollX,
          y: rect.bottom + window.scrollY + 10
        };
        console.log('📍 Calculated position from selection:', position);
      } else {
        console.log('⚠️ No selection range, using default position');
      }
    } catch (error) {
      console.error('❌ Error getting selection position:', error);
    }

    processText(request.action, request.text, position);
  }
});

// Add global functions to window for onclick handlers (kept for backward compatibility)
window.copyToClipboard = copyToClipboard;
window.replaceSelectedText = replaceSelectedText;