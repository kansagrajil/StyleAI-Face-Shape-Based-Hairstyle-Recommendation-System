/**
 * App — Global initialization, toast system, and loading overlay.
 * Loaded on every page to set up navbar auth state and shared utilities.
 */

// ── Toast System ────────────────────────────────────────────────
const AppToast = (() => {
    function show(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    return {
        success: (msg) => show(msg, 'success'),
        error:   (msg) => show(msg, 'error'),
        info:    (msg) => show(msg, 'info')
    };
})();

// ── Loading Overlay ─────────────────────────────────────────────
const AppLoading = (() => {
    function show(text = 'Processing...') {
        const overlay = document.getElementById('loadingOverlay');
        const textEl = document.getElementById('loadingText');
        if (overlay) {
            overlay.classList.add('active');
            if (textEl) textEl.textContent = text;
        }
    }

    function hide() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.remove('active');
    }

    return { show, hide };
})();

// ── Tab Switching (for analyze page) ────────────────────────────
function initTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;

            // Update active tab styles
            tabs.forEach(t => {
                t.classList.remove('active', 'btn-primary');
                t.classList.add('btn-outline-light');
            });
            tab.classList.add('active', 'btn-primary');
            tab.classList.remove('btn-outline-light');

            // Toggle panels using Bootstrap d-none class
            const uploadPanel = document.getElementById('uploadPanel');
            const webcamPanel = document.getElementById('webcamPanel');

            if (target === 'upload') {
                if (uploadPanel) uploadPanel.classList.remove('d-none');
                if (webcamPanel) webcamPanel.classList.add('d-none');

                // Release camera resources when navigating back to photo upload tab
                if (typeof Webcam !== 'undefined' && Webcam.stop) {
                    Webcam.stop();
                }
            } else {
                if (uploadPanel) uploadPanel.classList.add('d-none');
                if (webcamPanel) webcamPanel.classList.remove('d-none');
            }
        });
    });
}

// ── Global Init ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Update navbar auth state on every page
    if (typeof AppAuth !== 'undefined') {
        AppAuth.updateNavbar();
    }

    // Init tabs if present
    if (document.getElementById('inputTabs')) {
        initTabs();
    }

    // Add scroll effect to navbar
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (navbar) {
            if (window.scrollY > 10) {
                navbar.style.background = 'rgba(15, 23, 42, 0.95)';
            } else {
                navbar.style.background = 'rgba(15, 23, 42, 0.8)';
            }
        }
    });
});
