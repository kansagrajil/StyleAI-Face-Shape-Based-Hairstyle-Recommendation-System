/**
 * Authentication Module.
 * Handles login, register, logout, and navbar auth state.
 * Stores JWT token and user info in localStorage.
 */

const AppAuth = (() => {
    const STORAGE_KEYS = {
        token: 'styleai_token',
        userId: 'styleai_user_id',
        userName: 'styleai_user_name',
        guestId: 'styleai_guest_id'
    };

    /**
     * Get or generate persistent guest user ID (24-char hex string).
     * @returns {string}
     */
    function getGuestId() {
        let gid = localStorage.getItem(STORAGE_KEYS.guestId);
        if (!gid || gid.length !== 24) {
            // Generate valid 24-character hexadecimal ObjectId string
            const timestamp = Math.floor(Date.now() / 1000).toString(16).padStart(8, '0');
            const random = Array.from({length: 16}, () => Math.floor(Math.random() * 16).toString(16)).join('');
            gid = (timestamp + random).substring(0, 24);
            localStorage.setItem(STORAGE_KEYS.guestId, gid);
        }
        return gid;
    }

    /**
     * Check if the user is currently logged in.
     * @returns {boolean}
     */
    function isLoggedIn() {
        return !!localStorage.getItem(STORAGE_KEYS.token);
    }

    /**
     * Get the current user's display name.
     * @returns {string|null}
     */
    function getUserName() {
        return localStorage.getItem(STORAGE_KEYS.userName);
    }

    /**
     * Save auth data to localStorage.
     */
    function saveAuth(token, userId, name) {
        localStorage.setItem(STORAGE_KEYS.token, token);
        localStorage.setItem(STORAGE_KEYS.userId, userId);
        localStorage.setItem(STORAGE_KEYS.userName, name);
    }

    /**
     * Clear auth data from localStorage.
     */
    function clearAuth() {
        localStorage.removeItem(STORAGE_KEYS.token);
        localStorage.removeItem(STORAGE_KEYS.userId);
        localStorage.removeItem(STORAGE_KEYS.userName);
    }

    /**
     * Update the navbar to reflect auth state.
     */
    function updateNavbar() {
        const loginBtn = document.getElementById('navLoginBtn');
        const registerBtn = document.getElementById('navRegisterBtn');
        const userMenu = document.getElementById('navUserMenu');
        const userNameEl = document.getElementById('navUserName');

        if (!loginBtn || !userMenu) return;

        if (isLoggedIn()) {
            loginBtn.classList.add('hidden', 'd-none');
            if (registerBtn) registerBtn.classList.add('hidden', 'd-none');
            userMenu.classList.remove('hidden', 'd-none');
            userMenu.classList.add('d-flex');
            if (userNameEl) userNameEl.textContent = `👤 ${getUserName()}`;
        } else {
            loginBtn.classList.remove('hidden', 'd-none');
            if (registerBtn) registerBtn.classList.remove('hidden', 'd-none');
            userMenu.classList.add('hidden', 'd-none');
            userMenu.classList.remove('d-flex');
        }
    }

    /**
     * Handle login form submission.
     * @param {Event} e
     */
    async function login(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        const errorEl = document.getElementById('loginError');
        const submitBtn = document.getElementById('loginSubmitBtn');

        if (errorEl) {
            errorEl.classList.add('hidden', 'd-none');
            errorEl.textContent = '';
        }
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Logging in...';
        }

        try {
            const data = await API.post('/auth/login', { email, password });
            saveAuth(data.token, data.user_id, data.name);
            AppToast.success('Welcome back, ' + data.name + '!');
            setTimeout(() => {
                window.location.href = '/pages/analyze.html';
            }, 500);
        } catch (err) {
            if (errorEl) {
                errorEl.textContent = err.message || 'Login failed. Please check your credentials.';
                errorEl.classList.remove('hidden', 'd-none');
            }
            AppToast.error(err.message || 'Login failed');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Log In';
            }
        }
    }

    /**
     * Handle register form submission.
     * @param {Event} e
     */
    async function register(e) {
        e.preventDefault();
        const name = document.getElementById('regName').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const gender = document.getElementById('regGender').value;
        const password = document.getElementById('regPassword').value;
        const errorEl = document.getElementById('registerError');
        const submitBtn = document.getElementById('regSubmitBtn');

        if (errorEl) {
            errorEl.classList.add('hidden', 'd-none');
            errorEl.textContent = '';
        }
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating account...';
        }

        try {
            const data = await API.post('/auth/register', { name, email, password, gender });
            saveAuth(data.token, data.user_id, data.name);
            AppToast.success('Account created! Welcome, ' + data.name + '!');
            setTimeout(() => {
                window.location.href = '/pages/analyze.html';
            }, 500);
        } catch (err) {
            if (errorEl) {
                errorEl.textContent = err.message || 'Registration failed. Please try again.';
                errorEl.classList.remove('hidden', 'd-none');
            }
            AppToast.error(err.message || 'Registration failed');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Account';
            }
        }
    }

    /**
     * Log out the user.
     */
    function logout() {
        clearAuth();
        AppToast.info('You have been logged out.');
        setTimeout(() => {
            window.location.href = '/';
        }, 500);
    }

    /**
     * Redirect to login if not authenticated (for protected pages).
     * @returns {boolean} true if logged in.
     */
    function requireAuth() {
        if (!isLoggedIn()) {
            AppToast.error('Please log in to continue.');
            setTimeout(() => {
                window.location.href = '/pages/login.html';
            }, 1000);
            return false;
        }
        return true;
    }

    // Public API
    return { isLoggedIn, getUserName, getGuestId, login, register, logout, updateNavbar, requireAuth };
})();
