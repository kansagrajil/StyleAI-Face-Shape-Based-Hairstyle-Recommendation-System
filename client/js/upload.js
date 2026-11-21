/**
 * Upload Module.
 * Handles drag-and-drop and file input image upload,
 * client-side preview, and triggering the analysis API.
 */

const Upload = (() => {
    let selectedFile = null;

    /**
     * Initialize upload zone event listeners.
     */
    function init() {
        const zone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseFileBtn');

        if (!zone || !fileInput) return;

        // Click on zone or browse button
        zone.addEventListener('click', (e) => {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        if (browseBtn) {
            browseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                fileInput.click();
            });
        }

        // File selected via input
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        // Drag & drop visual cues
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('border-primary', 'bg-primary-subtle');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('border-primary', 'bg-primary-subtle');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('border-primary', 'bg-primary-subtle');
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    /**
     * Format file size for human-readable presentation.
     * @param {number} bytes
     * @returns {string}
     */
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Validate and preview the selected file.
     * @param {File} file
     */
    function handleFile(file) {
        // Validate type
        const allowed = ['image/jpeg', 'image/png', 'image/webp'];
        if (!allowed.includes(file.type)) {
            AppToast.error('Please upload a JPEG, PNG, or WebP image.');
            return;
        }

        // Validate size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            AppToast.error('Image must be smaller than 5MB.');
            return;
        }

        selectedFile = file;

        // Show preview and info
        const preview = document.getElementById('uploadPreview');
        const previewImg = document.getElementById('previewImage');
        const infoEl = document.getElementById('uploadFileInfo');

        if (preview && previewImg) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                preview.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        }

        if (infoEl) {
            infoEl.textContent = `${file.name} (${formatBytes(file.size)})`;
        }

        // Enable analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) analyzeBtn.disabled = false;

        AppToast.success('Image selected! Click "Analyze Face Geometry" to continue.');
    }

    /**
     * Set the selected file from an external source (e.g., webcam capture).
     * @param {File} file
     */
    function setFile(file) {
        selectedFile = file;
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) analyzeBtn.disabled = false;
    }

    /**
     * Clear selected file and hide preview cards.
     */
    function clearFile() {
        selectedFile = null;

        const fileInput = document.getElementById('fileInput');
        const uploadPreview = document.getElementById('uploadPreview');
        const capturePreview = document.getElementById('capturePreview');
        const analyzeBtn = document.getElementById('analyzeBtn');

        if (fileInput) fileInput.value = '';
        if (uploadPreview) uploadPreview.classList.add('d-none');
        if (capturePreview) capturePreview.classList.add('d-none');
        if (analyzeBtn) analyzeBtn.disabled = true;

        AppToast.info('Photo selection cleared.');
    }

    /**
     * Trigger the face analysis API call.
     */
    async function analyze() {
        if (!selectedFile) {
            AppToast.error('Please select or capture an image first.');
            return;
        }

        AppLoading.show('Extracting 468 3D facial mesh points...');

        const formData = new FormData();
        formData.append('image', selectedFile);

        const gender = document.getElementById('genderSelect');
        const hairType = document.getElementById('hairTypeSelect');
        if (gender) formData.append('gender', gender.value);
        if (hairType) formData.append('hair_type', hairType.value);

        try {
            const result = await API.postFormData('/analyze', formData);

            // Store result for results page
            sessionStorage.setItem('styleai_result', JSON.stringify(result));

            AppToast.success('Analysis complete! Preparing recommendations...');
            setTimeout(() => {
                window.location.href = '/pages/results.html';
            }, 600);
        } catch (err) {
            AppToast.error(err.message || 'Analysis failed. Please try again.');
        } finally {
            AppLoading.hide();
        }
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);

    return { handleFile, setFile, clearFile, analyze };
})();

