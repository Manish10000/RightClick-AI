# 🔄 Chrome Extension Reload Instructions

## ✅ **Changes Made - Extension Needs Reload**

The Chrome extension code has been updated to use the correct endpoints:
- **Fix Grammar** → `/chat/direct` (no RAG)
- **RAG Reply** → `/chat` (with RAG)

## 🔄 **How to Reload the Extension:**

### **Method 1: Extension Page Reload**
1. Open Chrome and go to `chrome://extensions/`
2. Find "AI Keyboard RAG Assistant"
3. Click the **🔄 reload icon** next to the extension
4. The extension will reload with the new code

### **Method 2: Toggle Extension**
1. Go to `chrome://extensions/`
2. **Turn OFF** the extension (toggle switch)
3. **Turn ON** the extension again
4. This forces a complete reload

### **Method 3: Remove and Re-add**
1. Go to `chrome://extensions/`
2. Click **"Remove"** on the extension
3. Click **"Load unpacked"** again
4. Select the `chrome-extension` folder

## 🧪 **Test After Reload:**

1. **Go to any webpage**
2. **Type:** "i want some good food so hungery"
3. **Select the text**
4. **Right-click** → "AI Keyboard Assistant" → "✏️ Fix Grammar"
5. **Check browser console (F12)** for logs:
   ```
   Processing action: fix-grammar Text: i want some good food so hungery... UseRAG: false
   Using endpoint: /chat/direct Request data: {message: "...", model: "llama3.1:8b"}
   ```

## ✅ **Expected Result:**
- **Fast grammar correction** without RAG
- **Console shows** `/chat/direct` endpoint
- **No document sources** in the response
- **Clean text replacement**

## 🚨 **If Still Not Working:**
1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Restart Chrome** completely
3. **Check console for errors** (F12 → Console tab)
4. **Verify server is running** on localhost:8000

The extension should now work perfectly with proper endpoint separation! 🎯