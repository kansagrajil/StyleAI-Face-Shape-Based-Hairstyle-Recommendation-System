/**
 * Virtual Try-On Studio Module.
 * Renders side-by-side virtual try-on comparison previews:
 * 1. Reference Portrait
 * 2. AI Try-On Synthetic Preview Result
 * 3. Hairstyle Reference Catalog Image
 */

const TryOn = (() => {
    let currentTryOnData = null;

    /**
     * Initialize try-on studio page on DOM load.
     */
    async function init() {
        const urlParams = new URLSearchParams(window.location.search);
        const tryonId = urlParams.get('id');

        if (tryonId) {
            // Fetch try-on record directly from API
            try {
                AppLoading.show('Retrieving virtual try-on record...');
                const data = await API.get(`/tryon/${tryonId}`);
                currentTryOnData = data;
                render(data);
            } catch (err) {
                console.error('Failed to fetch try-on result:', err);
                AppToast.error('Could not load try-on result.');
            } finally {
                AppLoading.hide();
            }
            return;
        }

        // Fall back to sessionStorage if present
        const raw = sessionStorage.getItem('styleai_tryon');
        if (!raw) {
            showEmptyState();
            return;
        }

        try {
            currentTryOnData = JSON.parse(raw);
            render(currentTryOnData);
        } catch (e) {
            console.error('Error rendering try-on session:', e);
            showEmptyState();
        }
    }

    function showEmptyState() {
        const resultEl = document.getElementById('tryonResult');
        const emptyEl = document.getElementById('tryonEmpty');
        if (resultEl) resultEl.classList.add('d-none');
        if (emptyEl) emptyEl.classList.remove('d-none');
    }

    /**
     * Render the virtual try-on result studio.
     * @param {Object} data - Try-on result object from API/sessionStorage.
     */
    function render(data) {
        if (!data) {
            showEmptyState();
            return;
        }

        const resultEl = document.getElementById('tryonResult');
        const emptyEl = document.getElementById('tryonEmpty');
        if (resultEl) resultEl.classList.remove('d-none');
        if (emptyEl) emptyEl.classList.add('d-none');

        // Titles and Text
        const titleEl = document.getElementById('tryonTitle');
        const hsNameEl = document.getElementById('tryonHairstyleName');
        const descEl = document.getElementById('tryonDescriptionText');
        const modelVerEl = document.getElementById('tryonModelVersion');
        const timeEl = document.getElementById('tryonMetaTime');
        const hsRefTitleEl = document.getElementById('hairstyleRefTitle');
        const faceBadgeEl = document.getElementById('tryonFaceShapeBadge');

        if (titleEl) titleEl.textContent = `${data.hairstyle_name || 'Hairstyle'} Try-On`;
        if (hsNameEl) hsNameEl.textContent = data.hairstyle_name || 'Virtual Hairstyle Preview';
        if (descEl) descEl.textContent = data.description || 'Personalized AI styling advice is ready for your face structure.';
        if (modelVerEl) modelVerEl.textContent = `Model: ${data.model_version || 'v1.0'}`;
        if (hsRefTitleEl) hsRefTitleEl.textContent = data.hairstyle_name || 'Catalog Reference';

        if (timeEl && data.generated_at) {
            const dt = new Date(data.generated_at).toLocaleString('en-US', {
                dateStyle: 'medium',
                timeStyle: 'short'
            });
            timeEl.innerHTML = `<i class="bi bi-clock me-1"></i>Generated: ${dt} (${data.processing_time_ms || 0}ms)`;
        }

        if (faceBadgeEl && data.face_shape) {
            const shapeStr = data.face_shape.toLowerCase();
            if (typeof FaceShapeHelper !== 'undefined') {
                faceBadgeEl.outerHTML = FaceShapeHelper.getBadgeHtml(shapeStr, true);
            } else {
                faceBadgeEl.textContent = `${shapeStr.toUpperCase()} SHAPE`;
            }
        }

        // Image Elements
        const userImgEl = document.getElementById('userImg');
        const tryonPreviewImgEl = document.getElementById('tryonPreviewImg');
        const hairstyleRefImgEl = document.getElementById('hairstyleRefImg');

        // 1. User original portrait
        if (userImgEl) {
            const userSrc = data.user_image || sessionStorage.getItem('styleai_user_image') || '/assets/images/faceshapes/oval.svg';
            userImgEl.src = userSrc;
        }

        // 2. Try-On Synthetic Preview Image (Crucial fix: use preview_url!)
        if (tryonPreviewImgEl) {
            const previewSrc = data.preview_url || data.hairstyle_image || '/assets/images/faceshapes/oval.svg';
            tryonPreviewImgEl.src = previewSrc;
        }

        // 3. Hairstyle Reference catalog image
        if (hairstyleRefImgEl) {
            const refSrc = data.hairstyle_image || data.preview_url || '/assets/images/faceshapes/oval.svg';
            hairstyleRefImgEl.src = refSrc;
        }
    }

    /**
     * Download the try-on preview image.
     */
    function downloadPreview() {
        if (!currentTryOnData || !currentTryOnData.preview_url) {
            AppToast.error('No preview image available to download.');
            return;
        }

        const link = document.createElement('a');
        link.href = currentTryOnData.preview_url;
        link.download = `StyleAI_TryOn_${(currentTryOnData.hairstyle_name || 'hairstyle').replace(/\s+/g, '_')}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        AppToast.success('Try-on preview download started!');
    }

    /**
     * Share try-on result link.
     */
    function shareResult() {
        const shareUrl = window.location.href;
        if (navigator.clipboard) {
            navigator.clipboard.writeText(shareUrl)
                .then(() => AppToast.success('Try-on studio link copied to clipboard!'))
                .catch(() => AppToast.info(`Share link: ${shareUrl}`));
        } else {
            AppToast.info(`Share link: ${shareUrl}`);
        }
    }

    /**
     * Navigate back to recommendations page.
     */
    function goBack() {
        window.location.href = '/pages/results.html';
    }

    // Initialize on DOM Ready
    document.addEventListener('DOMContentLoaded', init);

    return { downloadPreview, shareResult, goBack };
})();
