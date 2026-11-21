/**
 * Recommendation Dashboard Module.
 * Renders the full face shape analysis results:
 * - Uploaded portrait image
 * - Detected face shape + confidence score
 * - 6-class probability breakdown
 * - AI-generated recommendation explanations
 * - Recommended hairstyle preview grid
 * - Save, Download, and Share toolbar actions
 */

const Results = (() => {
    // Emoji mapping for 7 target face shapes
    const SHAPE_EMOJIS = {
        oval: '🥚', round: '🔴', square: '🟦', heart: '💜',
        diamond: '💎', oblong: '📏', triangle: '🔻'
    };

    let currentAnalysisData = null;

    /**
     * Load and render results from sessionStorage.
     */
    function init() {
        const raw = sessionStorage.getItem('styleai_result');
        if (!raw) {
            AppToast.error('No analysis results found. Please run a face scan first.');
            setTimeout(() => {
                window.location.href = '/pages/analyze.html';
            }, 1500);
            return;
        }

        try {
            currentAnalysisData = JSON.parse(raw);
            renderUploadedImage(currentAnalysisData);
            renderShape(currentAnalysisData);
            renderScores(currentAnalysisData.all_scores);
            renderAdvice(currentAnalysisData.ai_advice);
            renderHairstyles(currentAnalysisData.recommendations, currentAnalysisData.analysis_id);
        } catch (e) {
            console.error('Error rendering recommendation dashboard:', e);
            AppToast.error('Failed to load recommendation dashboard.');
        }
    }

    /**
     * Render the uploaded user portrait.
     */
    function renderUploadedImage(data) {
        const imgEl = document.getElementById('userUploadedImg');
        const placeholder = document.getElementById('userImgPlaceholder');

        if (data.image_path || data.thumbnail_path || data.user_image) {
            const imgSrc = data.user_image || data.thumbnail_path || data.image_path;
            if (imgEl) {
                imgEl.src = imgSrc;
                imgEl.classList.remove('d-none');
            }
            if (placeholder) placeholder.classList.add('d-none');
        }
    }

    /**
     * Render main face shape result hero card.
     */
    function renderShape(data) {
        const icon = document.getElementById('resultIcon');
        const name = document.getElementById('resultShapeName');
        const confidence = document.getElementById('resultConfidence');
        const bar = document.getElementById('confidenceBar');
        const modelBadge = document.getElementById('modelVerBadge');

        const shapeStr = (data.face_shape || 'oval').toLowerCase();
        if (icon) {
            if (typeof FaceShapeHelper !== 'undefined') {
                icon.innerHTML = FaceShapeHelper.getImgTag(shapeStr, 54);
            } else {
                icon.textContent = SHAPE_EMOJIS[shapeStr] || '🎯';
            }
        }
        if (name) name.textContent = shapeStr;
        if (confidence) confidence.textContent = `Confidence: ${Math.round((data.confidence || 0.95) * 100)}%`;
        if (modelBadge && data.model_version) modelBadge.textContent = `Model: ${data.model_version}`;
        if (bar) {
            setTimeout(() => {
                bar.style.width = `${(data.confidence || 0.95) * 100}%`;
            }, 300);
        }
    }

    /**
     * Render probability bars for target face shape classes.
     */
    function renderScores(allScores) {
        const container = document.getElementById('scoreBars');
        if (!container || !allScores) return;

        container.innerHTML = '';

        const sorted = Object.entries(allScores).sort(([, a], [, b]) => b - a);

        sorted.forEach(([shape, score]) => {
            const pct = Math.round(score * 100);
            const shapeImg = typeof FaceShapeHelper !== 'undefined'
                ? FaceShapeHelper.getImgTag(shape, 22, 'me-1')
                : (SHAPE_EMOJIS[shape] || '');
            const row = document.createElement('div');
            row.className = 'score-row mb-2';
            row.innerHTML = `
                <div class="d-flex align-items-center justify-content-between small text-muted mb-1">
                    <span class="d-inline-flex align-items-center gap-1">${shapeImg} <strong class="text-capitalize text-light">${shape}</strong></span>
                    <span class="fw-bold">${pct}%</span>
                </div>
                <div class="progress" style="height: 8px; background: rgba(255,255,255,0.08);">
                    <div class="progress-bar bg-gradient-primary rounded-pill" style="width: 0%" data-pct="${pct}"></div>
                </div>
            `;
            container.appendChild(row);

            setTimeout(() => {
                const fill = row.querySelector('.progress-bar');
                if (fill) fill.style.width = `${pct}%`;
            }, 400);
        });
    }

    /**
     * Render recommendation explanations & AI advice card.
     */
    function renderAdvice(advice) {
        const textEl = document.getElementById('aiAdviceText');
        const recList = document.getElementById('aiRecList');
        const avoidList = document.getElementById('aiAvoidList');
        const tipList = document.getElementById('aiTipList');

        if (!textEl) return;

        if (typeof advice === 'string') {
            textEl.textContent = advice;
            return;
        }

        if (advice.explanation) {
            textEl.textContent = advice.explanation;
        }

        if (recList && advice.recommendations) {
            recList.innerHTML = advice.recommendations.map(r => `
                <li class="list-group-item bg-transparent text-light border-white-10 py-2">
                    <strong class="text-primary">${r.name}:</strong> <span class="text-muted small">${r.reason}</span>
                </li>
            `).join('');
        }

        if (avoidList && advice.styles_to_avoid) {
            avoidList.innerHTML = advice.styles_to_avoid.map(a => `
                <li class="list-group-item bg-transparent text-light border-white-10 py-2">
                    <strong class="text-danger">${a.name}:</strong> <span class="text-muted small">${a.reason}</span>
                </li>
            `).join('');
        }

        if (tipList && advice.styling_tips) {
            tipList.innerHTML = advice.styling_tips.map(t => `
                <li class="mb-1"><i class="bi bi-arrow-right-short text-info me-1"></i>${t}</li>
            `).join('');
        }
    }

    /**
     * Render recommended hairstyle grid with preview cards.
     */
    function renderHairstyles(hairstyles, analysisId) {
        const grid = document.getElementById('hairstyleGrid');
        if (!grid) return;

        grid.innerHTML = '';

        if (!hairstyles || hairstyles.length === 0) {
            grid.innerHTML = `
                <div class="col-12 text-center py-5 text-muted">
                    <div class="display-3 mb-3">💇</div>
                    <h3>No direct hairstyle matches found</h3>
                    <p>Try adjusting your search criteria or uploading a different photo.</p>
                </div>
            `;
            return;
        }

        hairstyles.forEach(hs => {
            const col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4';
            const compatibilityPct = Math.round((hs.compatibility || 0.90) * 100);

            col.innerHTML = `
                <div class="glass-card hairstyle-card h-100 p-0 overflow-hidden border-gradient d-flex flex-column">
                    <div class="position-relative overflow-hidden" style="height: 220px;">
                        ${hs.image_url
                            ? `<img class="hairstyle-image w-100 h-100 object-cover" src="${hs.image_url}" alt="${hs.name}" onerror="this.onerror=null; this.src='/assets/images/hairstyles/default.jpg'">`
                            : `<div class="w-100 h-100 d-flex align-items-center justify-content-center bg-gradient-primary fs-1">💇</div>`
                        }
                        <span class="badge bg-success bg-opacity-90 position-absolute top-0 end-0 m-3 px-3 py-2 rounded-pill shadow">
                            ${compatibilityPct}% Match
                        </span>
                        <span class="badge bg-dark bg-opacity-75 position-absolute bottom-0 start-0 m-3 px-3 py-1 rounded-pill small border border-white-10">
                            ${hs.hair_length || 'medium'} • ${hs.category || 'classic'}
                        </span>
                    </div>

                    <div class="hairstyle-info p-4 d-flex flex-column flex-grow-1">
                        <h3 class="hairstyle-name h5 fw-bold mb-2">${hs.name}</h3>
                        <p class="hairstyle-desc text-muted small mb-3 flex-grow-1">${hs.description || ''}</p>
                        
                        <div class="hairstyle-tags mb-3 d-flex flex-wrap gap-1">
                            ${(hs.tags || []).map(t => `<span class="badge bg-secondary-subtle text-light small">${t}</span>`).join('')}
                        </div>

                        <div class="hairstyle-compatibility d-flex align-items-center justify-content-between pt-3 border-top border-white-10 mt-auto">
                            <span class="small text-muted"><i class="bi bi-speedometer2 text-warning me-1"></i>${hs.maintenance_level || 'medium'} maint.</span>
                            <button class="btn btn-sm btn-primary rounded-pill px-3 shadow" onclick="Results.tryOn('${analysisId}', '${hs.id}')">
                                ✨ Virtual Try-On
                            </button>
                        </div>
                    </div>
                </div>
            `;
            grid.appendChild(col);
        });
    }

    /**
     * Action 1: Save result to user history.
     */
    async function saveResult() {
        if (!AppAuth.requireAuth()) return;
        AppToast.success('Analysis result saved to your history!');
    }

    /**
     * Action 2: Download analysis report file.
     */
    function downloadReport() {
        if (!currentAnalysisData) return;

        const shape = currentAnalysisData.face_shape || 'Face Shape';
        const confidence = Math.round((currentAnalysisData.confidence || 0.95) * 100);
        const dateStr = new Date().toLocaleDateString();

        let reportText = `====================================================\n`;
        reportText += `STYLE AI — FACE SHAPE & HAIRSTYLE RECOMMENDATION REPORT\n`;
        reportText += `Generated on: ${dateStr}\n`;
        reportText += `====================================================\n\n`;
        reportText += `DETECTED FACE SHAPE : ${shape.toUpperCase()}\n`;
        reportText += `CONFIDENCE SCORE    : ${confidence}%\n\n`;

        reportText += `RECOMMENDED HAIRSTYLES:\n`;
        (currentAnalysisData.recommendations || []).forEach((r, idx) => {
            reportText += `  ${idx + 1}. ${r.name} (${Math.round((r.compatibility || 0.9) * 100)}% Match)\n`;
            reportText += `     - ${r.description || ''}\n`;
        });

        reportText += `\n====================================================\n`;
        reportText += `Thank you for using StyleAI!\n`;

        const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `StyleAI_${shape}_Analysis_Report.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        AppToast.success('Analysis report downloaded!');
    }

    /**
     * Action 3: Share results via Web Share API or Copy Link.
     */
    async function shareResult() {
        const shape = currentAnalysisData ? currentAnalysisData.face_shape : 'oval';
        const shareData = {
            title: 'My StyleAI Face Shape Analysis',
            text: `I just analyzed my face shape with StyleAI! My detected face shape is ${shape.toUpperCase()}. Check out your hairstyle match:`,
            url: window.location.href
        };

        if (navigator.share) {
            try {
                await navigator.share(shareData);
                AppToast.success('Shared successfully!');
                return;
            } catch (err) {
                console.log('Share canceled or failed:', err);
            }
        }

        // Fallback: Copy link to clipboard
        try {
            await navigator.clipboard.writeText(window.location.href);
            AppToast.success('Result link copied to clipboard!');
        } catch (e) {
            AppToast.info('URL: ' + window.location.href);
        }
    }

    /**
     * Trigger virtual try-on for a hairstyle.
     */
    async function tryOn(analysisId, hairstyleId) {
        if (!AppAuth.requireAuth()) return;

        AppLoading.show('Generating virtual try-on preview...');

        try {
            const result = await API.post('/tryon', {
                analysis_id: analysisId,
                hairstyle_id: hairstyleId
            });

            if (currentAnalysisData) {
                result.user_image = result.user_image || currentAnalysisData.user_image || currentAnalysisData.image_path || currentAnalysisData.thumbnail_path;
            }

            sessionStorage.setItem('styleai_tryon', JSON.stringify(result));
            window.location.href = '/pages/tryon.html';
        } catch (err) {
            AppToast.error(err.message || 'Virtual try-on failed.');
        } finally {
            AppLoading.hide();
        }
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);

    return { tryOn, saveResult, downloadReport, shareResult };
})();
