/**
 * History Module.
 * Fetches and renders paginated analysis history with real-time search,
 * face shape filtering, selected hairstyle tracking, view details, and deletion.
 */

const History = (() => {
    let currentPage = 1;
    const LIMIT = 10;
    let searchTimeout = null;

    const SHAPE_EMOJIS = {
        oval: '🥚', round: '🔴', square: '🟦', heart: '💜',
        diamond: '💎', oblong: '📏'
    };

    /**
     * Initialize the history page.
     */
    function init() {
        loadHistory();
    }

    /**
     * Fetch and render the history list.
     */
    async function loadHistory() {
        const listEl = document.getElementById('historyList');
        const emptyEl = document.getElementById('historyEmpty');
        const searchVal = (document.getElementById('historySearchInput')?.value || '').trim();
        const shapeVal = document.getElementById('historyShapeFilter')?.value || '';

        try {
            const data = await API.get('/history', {
                page: currentPage,
                limit: LIMIT,
                search: searchVal,
                shape: shapeVal
            });

            if (!data.analyses || data.analyses.length === 0) {
                if (listEl) listEl.innerHTML = '';
                if (emptyEl) emptyEl.classList.remove('d-none');
                updatePagination(0, 0);
                return;
            }

            if (emptyEl) emptyEl.classList.add('d-none');
            renderList(data.analyses);
            updatePagination(data.total, data.page);
        } catch (err) {
            console.error('Failed to load history:', err);
            AppToast.error(err.message || 'Failed to load history.');
        }
    }

    /**
     * Render history cards list.
     */
    function renderList(analyses) {
        const listEl = document.getElementById('historyList');
        if (!listEl) return;

        listEl.innerHTML = '';

        analyses.forEach(a => {
            const date = new Date(a.created_at).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });

            const shapeStr = (a.face_shape || 'oval').toLowerCase();
            const emoji = SHAPE_EMOJIS[shapeStr] || '🎯';
            const confidencePct = Math.round((a.confidence || 0.95) * 100);

            const selectedStyle = a.selected_hairstyle ? a.selected_hairstyle.name : null;

            const col = document.createElement('div');
            col.className = 'col-md-6';
            col.innerHTML = `
                <div class="glass-card p-4 h-100 border-gradient d-flex flex-column justify-content-between gap-3">
                    <div class="d-flex align-items-center justify-content-between gap-3 border-bottom border-white-10 pb-3">
                        <div class="d-flex align-items-center gap-3">
                            <div class="p-2 rounded-4 bg-primary-subtle text-primary border border-primary-subtle text-center d-flex align-items-center justify-content-center" style="width: 60px; height: 60px;">
                                ${typeof FaceShapeHelper !== 'undefined' ? FaceShapeHelper.getImgTag(shapeStr, 40) : emoji}
                            </div>
                            <div>
                                <span class="badge bg-primary text-uppercase">${shapeStr}</span>
                                <div class="fw-bold mt-1">Confidence: ${confidencePct}%</div>
                                <div class="small text-muted"><i class="bi bi-clock me-1"></i>${date}</div>
                            </div>
                        </div>
                    </div>

                    ${selectedStyle ? `
                        <div class="p-2 rounded-3 bg-success bg-opacity-10 border border-success-subtle small text-success">
                            <i class="bi bi-check-circle-fill me-1"></i>Selected Style: <strong>${selectedStyle}</strong>
                        </div>
                    ` : ''}

                    <div class="d-flex align-items-center justify-content-between pt-2">
                        <span class="small text-muted">${a.recommendations?.length || 0} recommendations</span>
                        <div class="d-flex align-items-center gap-2">
                            <button class="btn btn-sm btn-primary rounded-pill px-3 shadow" onclick="History.viewAnalysis('${a.analysis_id}')">
                                <i class="bi bi-eye-fill me-1"></i>View
                            </button>
                            <button class="btn btn-sm btn-outline-danger rounded-pill px-3" onclick="History.deleteAnalysis('${a.analysis_id}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
            listEl.appendChild(col);
        });
    }

    /**
     * Debounced search handler.
     */
    function onSearchInput() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentPage = 1;
            loadHistory();
        }, 400);
    }

    /**
     * Filter dropdown change handler.
     */
    function onFilterChange() {
        currentPage = 1;
        loadHistory();
    }

    /**
     * Update pagination controls.
     */
    function updatePagination(total, page) {
        const pageInfo = document.getElementById('pageInfo');
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        const totalPages = Math.ceil(total / LIMIT) || 1;

        if (pageInfo) pageInfo.textContent = `Page ${page || 1} of ${totalPages}`;
        if (prevBtn) prevBtn.disabled = (page || 1) <= 1;
        if (nextBtn) nextBtn.disabled = (page || 1) >= totalPages;
    }

    function prevPage() {
        if (currentPage > 1) {
            currentPage--;
            loadHistory();
        }
    }

    function nextPage() {
        currentPage++;
        loadHistory();
    }

    /**
     * View specific analysis detail.
     */
    async function viewAnalysis(analysisId) {
        try {
            const data = await API.get(`/history/${analysisId}`);
            sessionStorage.setItem('styleai_result', JSON.stringify(data));
            window.location.href = '/pages/results.html';
        } catch (err) {
            AppToast.error('Failed to load analysis detail.');
        }
    }

    /**
     * Delete single analysis entry.
     */
    async function deleteAnalysis(analysisId) {
        if (!confirm('Are you sure you want to delete this scan record from history?')) return;

        try {
            await API.del(`/history/${analysisId}`);
            AppToast.success('Analysis history deleted.');
            loadHistory();
        } catch (err) {
            AppToast.error(err.message || 'Failed to delete record.');
        }
    }

    /**
     * Bulk clear user history.
     */
    async function clearAllHistory() {
        if (!confirm('Are you sure you want to CLEAR ALL your analysis history records? This action cannot be undone.')) return;

        try {
            await API.del('/history');
            AppToast.success('All history records cleared.');
            loadHistory();
        } catch (err) {
            AppToast.error(err.message || 'Failed to clear history.');
        }
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);

    return {
        prevPage, nextPage, viewAnalysis, deleteAnalysis, clearAllHistory,
        onSearchInput, onFilterChange
    };
})();
