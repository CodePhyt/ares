/**
 * JavaScript/Node.js client for ARES API
 */

class ARESClient {
    constructor(baseUrl = 'http://localhost:8000', options = {}) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiUrl = `${this.baseUrl}/api/v1`;
        this.timeout = options.timeout || 120000;
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
    }

    async _request(method, endpoint, data = null, isFile = false) {
        const url = `${this.apiUrl}${endpoint}`;
        const config = {
            method,
            headers: {},
            signal: AbortSignal.timeout(this.timeout),
        };

        if (isFile) {
            // For file uploads, use FormData
            const formData = new FormData();
            formData.append('file', data);
            config.body = formData;
        } else if (data) {
            config.headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(data);
        }

        for (let attempt = 0; attempt < this.maxRetries; attempt++) {
            try {
                const response = await fetch(url, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                if (attempt < this.maxRetries - 1) {
                    console.warn(`Request failed, retrying... (${attempt + 1}/${this.maxRetries})`);
                    await this._sleep(this.retryDelay * (attempt + 1));
                } else {
                    throw error;
                }
            }
        }
    }

    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }

    async query(query, maskPii = true) {
        return await this._request('POST', '/query', {
            query,
            mask_pii: maskPii,
        });
    }

    async uploadDocument(file) {
        return await this._request('POST', '/upload', file, true);
    }

    async deleteDocument(documentId) {
        return await this._request('DELETE', `/documents/${documentId}`);
    }

    async detectPII(text) {
        return await this._request('POST', '/pii/detect', { text });
    }

    async maskPII(text) {
        return await this._request('POST', '/pii/mask', { text });
    }

    async getStats() {
        return await this._request('GET', '/stats');
    }

    async getMetrics() {
        return await this._request('GET', '/metrics');
    }
}

// Example usage (Node.js with node-fetch or browser)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ARESClient;
}

// Browser usage example:
/*
const client = new ARESClient('http://localhost:8000');

// Health check
const health = await client.healthCheck();
console.log('Status:', health.status);

// Query documents
const result = await client.query('What is the main topic?');
console.log('Answer:', result.answer);
console.log('Confidence:', result.confidence);

// Upload document
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];
const uploadResult = await client.uploadDocument(file);
console.log('Document ID:', uploadResult.document_id);
*/
