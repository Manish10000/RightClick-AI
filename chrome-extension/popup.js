// AI Keyboard RAG Assistant - Popup Script

class AIKeyboardPopup {
  constructor() {
    this.baseUrl = 'http://localhost:8000';
    this.accessToken = '';
    this.refreshToken = '';
    this.init();
  }

  async init() {
    await this.loadSettings();
    this.setupEventListeners();
    this.setupTabs();
    await this.checkAuthStatus();
    await this.loadDocuments();
  }

  async loadSettings() {
    const result = await chrome.storage.sync.get(['baseUrl', 'accessToken', 'refreshToken']);
    this.baseUrl = result.baseUrl || 'http://localhost:8000';
    this.accessToken = result.accessToken || '';
    this.refreshToken = result.refreshToken || '';
    
    document.getElementById('baseUrl').value = this.baseUrl;
  }

  async saveSettings() {
    this.baseUrl = document.getElementById('baseUrl').value;
    await chrome.storage.sync.set({
      baseUrl: this.baseUrl,
      accessToken: this.accessToken,
      refreshToken: this.refreshToken
    });
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.makeAPIRequest('/auth/refresh', 'POST', {
      refresh_token: this.refreshToken
    });

    this.accessToken = response.access_token;
    await this.saveSettings();
    return response.access_token;
  }

  setupEventListeners() {
    // Settings
    document.getElementById('baseUrl').addEventListener('change', () => this.saveSettings());
    document.getElementById('testConnection').addEventListener('click', () => this.testConnection());

    // Upload
    document.getElementById('browseFiles').addEventListener('click', () => {
      document.getElementById('fileInput').click();
    });
    document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileSelect(e));
    
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
    uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
    uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

    // Documents
    document.getElementById('refreshDocs').addEventListener('click', () => this.loadDocuments());

    // Auth
    document.getElementById('loginBtn').addEventListener('click', () => this.login());
    document.getElementById('registerBtn').addEventListener('click', () => this.register());
    document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
  }

  setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        
        // Remove active class from all tabs and contents
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding content
        btn.classList.add('active');
        document.getElementById(tabId).classList.add('active');
      });
    });
  }

  async makeAPIRequest(endpoint, method = 'GET', data = null, isFormData = false) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const options = {
      method,
      headers: {}
    };

    // Set content type only for JSON requests
    if (!isFormData) {
      options.headers['Content-Type'] = 'application/json';
    }

    if (this.accessToken) {
      options.headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    if (data) {
      if (isFormData) {
        options.body = data; // FormData object
      } else {
        options.body = JSON.stringify(data);
      }
    }

    // Show loading indicator
    this.showGlobalLoader(true);

    try {
      const response = await fetch(url, options);
      
      // Handle 401 Unauthorized - try to refresh token
      if (response.status === 401 && this.refreshToken && endpoint !== '/auth/refresh') {
        try {
          await this.refreshAccessToken();
          // Retry the original request with new token
          options.headers['Authorization'] = `Bearer ${this.accessToken}`;
          const retryResponse = await fetch(url, options);
          if (!retryResponse.ok) {
            throw new Error(`HTTP error! status: ${retryResponse.status}`);
          }
          return await retryResponse.json();
        } catch (refreshError) {
          // Refresh failed, clear tokens and show login
          this.accessToken = '';
          this.refreshToken = '';
          await this.saveSettings();
          this.showLoginSection();
          throw new Error('Session expired. Please login again.');
        }
      }

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
    } finally {
      // Hide loading indicator
      this.showGlobalLoader(false);
    }
  }

  showGlobalLoader(show) {
    let loader = document.getElementById('global-loader');
    
    if (show) {
      if (!loader) {
        loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'global-loader';
        loader.innerHTML = `
          <div class="global-loader-backdrop"></div>
          <div class="global-loader-content">
            <div class="global-loader-spinner"></div>
            <div class="global-loader-text">Processing...</div>
          </div>
        `;
        document.body.appendChild(loader);
      }
      loader.style.display = 'flex';
    } else {
      if (loader) {
        loader.style.display = 'none';
      }
    }
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.makeAPIRequest('/auth/refresh', 'POST', {
      refresh_token: this.refreshToken
    });

    this.accessToken = response.access_token;
    await this.saveSettings();
    return response.access_token;
  }

  async testConnection() {
    const statusEl = document.getElementById('connectionStatus');
    statusEl.textContent = 'Testing connection...';
    statusEl.className = 'status info';

    try {
      // Test health endpoint without authentication
      const url = `${this.baseUrl}/health`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      statusEl.textContent = `✅ Connected successfully! Server: ${data.status}`;
      statusEl.className = 'status success';
    } catch (error) {
      statusEl.textContent = `❌ Connection failed: ${error.message}`;
      statusEl.className = 'status error';
    }
  }

  // File Upload Handlers
  handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.add('dragover');
  }

  handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('dragover');
  }

  handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    this.uploadFiles(files);
  }

  handleFileSelect(e) {
    const files = Array.from(e.target.files);
    this.uploadFiles(files);
  }

  async uploadFiles(files) {
    if (files.length === 0) return;

    // Validate files
    const allowedExtensions = ['.pdf', '.txt', '.md'];
    const maxFileSize = 50 * 1024 * 1024; // 50MB
    
    for (const file of files) {
      const extension = '.' + file.name.split('.').pop().toLowerCase();
      if (!allowedExtensions.includes(extension)) {
        const statusEl = document.getElementById('uploadStatus');
        statusEl.textContent = `❌ Unsupported file type: ${file.name}. Allowed: PDF, TXT, MD`;
        statusEl.className = 'status error';
        return;
      }
      
      if (file.size > maxFileSize) {
        const statusEl = document.getElementById('uploadStatus');
        statusEl.textContent = `❌ File too large: ${file.name}. Maximum size: 50MB`;
        statusEl.className = 'status error';
        return;
      }
    }

    // Check if user is logged in
    if (!this.accessToken) {
      const statusEl = document.getElementById('uploadStatus');
      statusEl.textContent = '❌ Please login first to upload documents';
      statusEl.className = 'status error';
      return;
    }

    const progressContainer = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const statusEl = document.getElementById('uploadStatus');

    progressContainer.style.display = 'block';
    statusEl.textContent = '';

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const progress = ((i + 1) / files.length) * 100;
        
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `Uploading ${file.name}... (${i + 1}/${files.length})`;

        await this.uploadSingleFile(file);
      }

      statusEl.textContent = `✅ Successfully uploaded ${files.length} file(s)`;
      statusEl.className = 'status success';
      
      // Refresh documents list
      await this.loadDocuments();
      
      // Clear file input
      document.getElementById('fileInput').value = '';
      
    } catch (error) {
      statusEl.textContent = `❌ Upload failed: ${error.message}`;
      statusEl.className = 'status error';
    } finally {
      progressContainer.style.display = 'none';
    }
  }

  async uploadSingleFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      headers: this.accessToken ? {
        'Authorization': `Bearer ${this.accessToken}`
      } : {},
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.message || `Upload failed: ${response.status}`;
      } catch {
        errorMessage = `Upload failed: ${response.status}`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  }

  async loadDocuments() {
    const listEl = document.getElementById('documentsList');
    listEl.innerHTML = '<div class="loading">Loading documents...</div>';

    try {
      const response = await this.makeAPIRequest('/documents');
      this.renderDocuments(response.documents);
    } catch (error) {
      listEl.innerHTML = `<div class="status error">Failed to load documents: ${error.message}</div>`;
    }
  }

  renderDocuments(documents) {
    const listEl = document.getElementById('documentsList');
    
    if (documents.length === 0) {
      listEl.innerHTML = '<div class="status info">No documents uploaded yet. Upload some PDFs to enable RAG functionality.</div>';
      return;
    }

    listEl.innerHTML = documents.map(doc => `
      <div class="document-item">
        <div class="document-info">
          <div class="document-name" title="${doc.file_name}">${doc.file_name}</div>
          <div class="document-meta">
            ${doc.num_chunks} chunks${doc.total_pages ? ` • ${doc.total_pages} pages` : ''} • 
            ${new Date(doc.uploaded_at).toLocaleDateString()}
          </div>
        </div>
        <div class="document-actions">
          <button class="btn btn-danger btn-small delete-doc-btn" data-doc-id="${doc.id}" data-file-name="${doc.file_name}">Delete</button>
        </div>
      </div>
    `).join('');

    // Add event listeners to delete buttons
    const deleteButtons = listEl.querySelectorAll('.delete-doc-btn');
    deleteButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const docId = e.target.dataset.docId;
        const fileName = e.target.dataset.fileName;
        this.deleteDocument(docId, fileName);
      });
    });
  }

  async deleteDocument(docId, fileName) {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) return;

    try {
      await this.makeAPIRequest(`/documents/${docId}`, 'DELETE');
      await this.loadDocuments();
      
      // Show success message
      const statusEl = document.getElementById('uploadStatus');
      statusEl.textContent = `✅ Document "${fileName}" deleted successfully`;
      statusEl.className = 'status success';
      
      // Clear status after 3 seconds
      setTimeout(() => {
        statusEl.textContent = '';
        statusEl.className = 'status';
      }, 3000);
      
    } catch (error) {
      alert(`Failed to delete document: ${error.message}`);
    }
  }

  // Authentication
  async checkAuthStatus() {
    if (!this.accessToken) {
      this.showLoginSection();
      return;
    }

    try {
      const user = await this.makeAPIRequest('/auth/me');
      this.showUserSection(user);
    } catch (error) {
      this.accessToken = '';
      await this.saveSettings();
      this.showLoginSection();
    }
  }

  async login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const statusEl = document.getElementById('authStatus');

    if (!email || !password) {
      statusEl.textContent = 'Please enter email and password';
      statusEl.className = 'status error';
      return;
    }

    try {
      const response = await this.makeAPIRequest('/auth/login', 'POST', {
        email,
        password
      });

      this.accessToken = response.access_token;
      this.refreshToken = response.refresh_token;
      await this.saveSettings();
      
      statusEl.textContent = 'Login successful!';
      statusEl.className = 'status success';
      
      // Clear form
      document.getElementById('email').value = '';
      document.getElementById('password').value = '';
      
      await this.checkAuthStatus();
      await this.loadDocuments();
      
    } catch (error) {
      statusEl.textContent = `Login failed: ${error.message}`;
      statusEl.className = 'status error';
    }
  }

  async register() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const statusEl = document.getElementById('authStatus');

    if (!email || !password) {
      statusEl.textContent = 'Please enter email and password';
      statusEl.className = 'status error';
      return;
    }

    if (password.length < 8) {
      statusEl.textContent = 'Password must be at least 8 characters';
      statusEl.className = 'status error';
      return;
    }

    try {
      const response = await this.makeAPIRequest('/auth/register', 'POST', {
        email,
        password
      });

      this.accessToken = response.access_token;
      this.refreshToken = response.refresh_token;
      await this.saveSettings();
      
      statusEl.textContent = 'Registration successful!';
      statusEl.className = 'status success';
      
      // Clear form
      document.getElementById('email').value = '';
      document.getElementById('password').value = '';
      
      await this.checkAuthStatus();
      
    } catch (error) {
      statusEl.textContent = `Registration failed: ${error.message}`;
      statusEl.className = 'status error';
    }
  }

  async logout() {
    try {
      if (this.refreshToken) {
        await this.makeAPIRequest('/auth/logout', 'POST', {
          refresh_token: this.refreshToken
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    }

    this.accessToken = '';
    this.refreshToken = '';
    await this.saveSettings();
    this.showLoginSection();
    
    // Clear documents list
    document.getElementById('documentsList').innerHTML = '<div class="loading">Please login to view documents</div>';
    
    // Clear auth status
    document.getElementById('authStatus').textContent = '';
    document.getElementById('authStatus').className = 'status';
  }

  showLoginSection() {
    document.getElementById('loginSection').style.display = 'block';
    document.getElementById('userSection').style.display = 'none';
  }

  showUserSection(user) {
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('userSection').style.display = 'block';
    
    document.getElementById('userInfo').innerHTML = `
      <p><strong>Email:</strong> ${user.email}</p>
      <p><strong>Name:</strong> ${user.full_name || 'Not set'}</p>
      <p><strong>Status:</strong> ${user.is_active ? 'Active' : 'Inactive'}</p>
    `;
  }
}

// Initialize popup
const popup = new AIKeyboardPopup();