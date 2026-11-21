/**
 * API Service — Centralized HTTP client.
 * Wraps the Fetch API with automatic JWT injection,
 * error handling, and base URL management.
 */

const API = (() => {
    const BASE_URL = '/api';

    /**
     * Get stored JWT token from localStorage.
     * @returns {string|null}
     */
    function getToken() {
        return localStorage.getItem('styleai_token');
    }

    /**
     * Build request headers with optional auth token.
     * @param {boolean} isJson - Whether to set Content-Type to JSON.
     * @returns {Headers}
     */
    function buildHeaders(isJson = true) {
        const headers = new Headers();
        const token = getToken();

        if (token) {
            headers.set('Authorization', `Bearer ${token}`);
        }
        if (typeof AppAuth !== 'undefined' && AppAuth.getGuestId) {
            headers.set('X-Guest-ID', AppAuth.getGuestId());
        }
        if (isJson) {
            headers.set('Content-Type', 'application/json');
        }
        return headers;
    }

    /**
     * Handle API response — parse JSON and throw on error status.
     * @param {Response} response
     * @returns {Promise<Object>}
     */
    async function handleResponse(response) {
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            const error = new Error(data.error || data.message || `HTTP ${response.status}`);
            error.status = response.status;
            error.data = data;
            throw error;
        }
        return data;
    }

    /**
     * GET request.
     * @param {string} endpoint - API path (e.g., '/history').
     * @param {Object} params - Optional query parameters.
     * @returns {Promise<Object>}
     */
    async function get(endpoint, params = {}) {
        const url = new URL(BASE_URL + endpoint, window.location.origin);
        Object.entries(params).forEach(([key, val]) => {
            if (val !== undefined && val !== null && val !== '') {
                url.searchParams.set(key, val);
            }
        });

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: buildHeaders()
        });
        return handleResponse(response);
    }

    /**
     * POST request with JSON body.
     * @param {string} endpoint
     * @param {Object} body
     * @returns {Promise<Object>}
     */
    async function post(endpoint, body = {}) {
        const response = await fetch(BASE_URL + endpoint, {
            method: 'POST',
            headers: buildHeaders(true),
            body: JSON.stringify(body)
        });
        return handleResponse(response);
    }

    /**
     * POST request with FormData (multipart/form-data).
     * Used for file uploads.
     * @param {string} endpoint
     * @param {FormData} formData
     * @returns {Promise<Object>}
     */
    async function postFormData(endpoint, formData) {
        const headers = new Headers();
        const token = getToken();
        if (token) {
            headers.set('Authorization', `Bearer ${token}`);
        }
        if (typeof AppAuth !== 'undefined' && AppAuth.getGuestId) {
            headers.set('X-Guest-ID', AppAuth.getGuestId());
        }
        // Don't set Content-Type — browser sets it with boundary for FormData

        const response = await fetch(BASE_URL + endpoint, {
            method: 'POST',
            headers: headers,
            body: formData
        });
        return handleResponse(response);
    }

    /**
     * DELETE request.
     * @param {string} endpoint
     * @returns {Promise<Object>}
     */
    async function del(endpoint) {
        const response = await fetch(BASE_URL + endpoint, {
            method: 'DELETE',
            headers: buildHeaders()
        });
        return handleResponse(response);
    }

    // Public API
    return { get, post, postFormData, del, getToken };
})();
