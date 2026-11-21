/**
 * Dashboard Logic — Fetches user history and profile metrics to render dashboard widgets.
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Require authentication
    if (typeof AppAuth !== 'undefined' && !AppAuth.isLoggedIn()) {
        AppAuth.requireAuth();
        return;
    }

    const userName = AppAuth.getUserName() || 'Stylist';
    const greetingEl = document.getElementById('dashUserGreeting');
    if (greetingEl) greetingEl.textContent = userName;

    try {
        // Fetch recent analysis history from backend API
        const historyData = await API.get('/history');
        const analyses = historyData.analyses || [];

        // Update stats counters
        const totalScansEl = document.getElementById('dashTotalScans');
        const primaryShapeEl = document.getElementById('dashPrimaryShape');
        if (totalScansEl) totalScansEl.textContent = analyses.length;

        if (analyses.length > 0) {
            const latest = analyses[0];
            if (primaryShapeEl) primaryShapeEl.textContent = latest.face_shape.toUpperCase();

            // Render Recent Scan Widget
            const container = document.getElementById('dashRecentScanContainer');
            if (container) {
                container.innerHTML = `
                    <div class="d-flex align-items-center gap-3 p-3 rounded-4 bg-dark-subtle border border-white-10 mb-3">
                        <div>${typeof FaceShapeHelper !== 'undefined' ? FaceShapeHelper.getImgTag(latest.face_shape, 42) : '👤'}</div>
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge bg-primary text-uppercase">${latest.face_shape} Shape</span>
                                <span class="small text-muted">${new Date(latest.created_at).toLocaleDateString()}</span>
                            </div>
                            <div class="fw-bold mt-1">Confidence Score: ${(latest.confidence * 100).toFixed(1)}%</div>
                            <p class="small text-muted mb-0 line-clamp-2 mt-1">${latest.ai_advice || 'Personalized hairstyle recommendations ready.'}</p>
                        </div>
                        <a href="results.html?id=${latest.analysis_id}" class="btn btn-outline-primary btn-sm rounded-pill px-3">View Details</a>
                    </div>
                `;
            }
        }
    } catch (err) {
        console.error('Failed to load dashboard data:', err);
    }
});
