# AI Keyboard Chrome Extension

A Chrome extension that provides AI-powered text processing with RAG (Retrieval-Augmented Generation) capabilities directly in your browser.

## Features

- **Context Menu Integration**: Right-click on selected text for AI processing
- **Multiple AI Actions**: Grammar correction, professional rewriting, RAG replies, and text description
- **Document-Based Responses**: Upload your documents for personalized, contextual AI responses
- **Auto-Replace**: Selected text is automatically replaced with AI-generated content
- **Clipboard Integration**: Results are automatically copied to clipboard
- **Popup Interface**: Manage settings, authentication, and document uploads
- **Loading Indicators**: Visual feedback during AI processing
- **Markdown Rendering**: Properly formatted AI responses with text selection

## Installation

### From Source
1. Download or clone the extension files
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked" and select the `chrome-extension` folder
5. The AI Keyboard icon should appear in your Chrome toolbar

## Setup

### 1. Configure Server Connection
1. Click the AI Keyboard extension icon
2. Set the **Base URL** to your RAG server (default: `http://localhost:8000`)
3. Click "Test Connection" to verify connectivity

### 2. Authentication
1. **Register**: Create a new account with email and password
2. **Login**: Sign in with your credentials
3. The extension will remember your login session

### 3. Upload Documents (Optional)
1. Click "Upload Document" in the extension popup
2. Select PDF or text files containing your personal information
3. Documents are processed and stored securely for RAG functionality

## Usage

### Text Processing Actions

#### 1. Fix Grammar
- **Purpose**: Corrects grammar, spelling, and punctuation
- **Usage**: Select text → Right-click → "Fix Grammar"
- **Example**: "i want some good food" → "I want some good food"
- **Endpoint**: `/chat/direct` (no RAG)

#### 2. RAG Reply
- **Purpose**: Provides contextual responses using your uploaded documents
- **Usage**: Select text → Right-click → "RAG Reply"
- **Example**: "What have you worked on?" → Personalized response based on your resume
- **Endpoint**: `/chat` (with RAG)

#### 3. General Reply
- **Purpose**: Provides general AI responses without document context
- **Usage**: Select text → Right-click → "General Reply"
- **Example**: "What is Python?" → General explanation of Python
- **Endpoint**: `/chat/direct` (no RAG)

#### 4. Make Professional & Polite
- **Purpose**: Rewrites text in a professional, formal tone
- **Usage**: Select text → Right-click → "Make Professional & Polite"
- **Example**: "hey can u help me" → "Hello, could you please assist me?"
- **Endpoint**: `/chat/direct` (no RAG)

#### 5. Describe
- **Purpose**: Provides detailed explanations of selected text
- **Usage**: Select text → Right-click → "Describe"
- **Result**: Shows explanation in a popup window (doesn't replace text)
- **Endpoint**: `/chat/direct` (no RAG)

### Popup Interface Features

#### Settings Tab
- **Base URL**: Configure your RAG server endpoint
- **Test Connection**: Verify server connectivity
- **Auto-save**: Settings are automatically saved

#### Authentication Tab
- **Register**: Create new account
- **Login**: Sign in to existing account
- **Logout**: Clear session and credentials

#### Documents Tab
- **Upload**: Add PDF/text documents for RAG functionality
- **List**: View uploaded documents
- **Delete**: Remove documents from your account

## File Structure

```
chrome-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker for context menu
├── content.js            # Content script for text processing
├── popup.html            # Extension popup interface
├── popup.js              # Popup functionality
├── popup.css             # Popup styling
├── content.css           # Content script styling
└── icons/                # Extension icons
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## Technical Details

### Permissions
- `activeTab`: Access current tab for text processing
- `contextMenus`: Add right-click menu options
- `storage`: Save settings and authentication tokens
- `host_permissions`: Access to configured server URL

### API Integration
- **Authentication**: JWT tokens stored securely
- **File Upload**: Multipart form data for document upload
- **Text Processing**: JSON requests to various AI endpoints
- **Error Handling**: User-friendly error messages and fallbacks

### Text Processing Flow
1. User selects text on webpage
2. Right-click opens context menu with AI options
3. Extension captures selected text and position
4. Loading indicator shows on cursor
5. API request sent to configured server
6. AI response received and processed
7. Text automatically replaced and copied to clipboard
8. Success notification shown

### Response Handling
- **Auto-Replace Actions**: Grammar, Professional, General Reply, RAG Reply
- **Popup Actions**: Describe (shows in popup window)
- **Markdown Rendering**: Converts AI responses to formatted HTML
- **Text Selection**: Users can select and copy parts of AI responses
- **Clipboard Integration**: Automatic copying for easy pasting elsewhere

## Customization

### Adding New Actions
1. Add menu item in `background.js`:
```javascript
chrome.contextMenus.create({
  id: "new-action",
  title: "New Action",
  contexts: ["selection"]
});
```

2. Handle action in `content.js`:
```javascript
case 'new-action':
  prompt = `Your custom prompt: "${text}"`;
  useRAG = false; // or true for RAG
  autoReplace = true; // or false for popup
  break;
```

### Styling Modifications
- Edit `popup.css` for popup interface styling
- Edit `content.css` for result window and notification styling
- Modify `popup.html` for interface layout changes

## Troubleshooting

### Common Issues

1. **Extension not loading**
   - Check `chrome://extensions/` for error messages
   - Ensure all files are present in the extension folder
   - Try reloading the extension

2. **Context menu not appearing**
   - Verify text is selected before right-clicking
   - Check if extension is enabled
   - Reload the webpage

3. **API connection failed**
   - Verify server is running at configured URL
   - Check Base URL in extension settings
   - Test connection using the "Test Connection" button

4. **Authentication errors**
   - Re-login through the extension popup
   - Check server logs for authentication issues
   - Clear extension storage and re-authenticate

5. **Text not replacing**
   - Ensure text remains selected during processing
   - Check browser console for JavaScript errors
   - Try refreshing the page and selecting text again

6. **Popup not showing for Describe**
   - Check if popup is blocked by other page elements
   - Look for the popup window (it may be positioned off-screen)
   - Try using Describe on different text/pages

### Debug Mode
1. Open Chrome DevTools (F12)
2. Check Console tab for error messages
3. Look for extension-related logs prefixed with emojis (📨, ✅, ❌)

### Reset Extension
1. Go to `chrome://extensions/`
2. Click "Remove" on AI Keyboard extension
3. Reload the extension from the folder
4. Reconfigure settings and re-authenticate

## Development

### Testing Changes
1. Make code changes
2. Go to `chrome://extensions/`
3. Click the refresh icon on AI Keyboard extension
4. Test functionality on any webpage

### Adding Features
- Modify `manifest.json` for new permissions
- Update `background.js` for new context menu items
- Extend `content.js` for new text processing logic
- Enhance `popup.js` for new interface features

## Security

- JWT tokens stored in Chrome's secure storage
- All API communications over HTTPS (in production)
- User data isolated per account
- No sensitive data stored in extension code
- Automatic token refresh handling