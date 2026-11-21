/**
 * Webcam Capture Module.
 * Accesses the user's camera via MediaDevices API,
 * captures a frame to canvas, and converts to a File for upload.
 */

const Webcam = (() => {
    let stream = null;

    /**
     * Check if mediaDevices API is supported in the current environment.
     * @returns {boolean}
     */
    function isSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }

    /**
     * Start the webcam feed.
     */
    async function start() {
        if (!isSupported()) {
            AppToast.error('Webcam API is not supported by your browser or secure context (HTTPS required).');
            return;
        }

        const video = document.getElementById('webcamFeed');
        const startBtn = document.getElementById('startWebcamBtn');
        const captureBtn = document.getElementById('captureBtn');
        const stopBtn = document.getElementById('stopWebcamBtn');
        const badge = document.getElementById('cameraActiveBadge');
        const capturePreview = document.getElementById('capturePreview');

        if (!video) return;

        try {
            // Stop any existing stream before starting a new one
            if (stream) {
                stop();
            }

            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280, min: 640 },
                    height: { ideal: 720, min: 480 },
                    facingMode: 'user'
                },
                audio: false
            });

            video.srcObject = stream;
            await video.play().catch(() => {});

            // Update UI controls using Bootstrap d-none class
            if (startBtn) startBtn.classList.add('d-none');
            if (captureBtn) {
                captureBtn.classList.remove('d-none');
                captureBtn.classList.add('d-flex');
            }
            if (stopBtn) stopBtn.classList.remove('d-none');
            if (badge) badge.classList.remove('d-none');
            if (capturePreview) capturePreview.classList.add('d-none');

            AppToast.info('Camera active! Position your face in center frame and click capture.');
        } catch (err) {
            console.error('Webcam error:', err);
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                AppToast.error('Camera access denied. Please grant camera permissions in your browser.');
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                AppToast.error('No webcam device found on your computer.');
            } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                AppToast.error('Camera is currently in use by another application.');
            } else {
                AppToast.error('Failed to access camera: ' + err.message);
            }
        }
    }

    /**
     * Capture a frame from the video feed.
     */
    function capture() {
        const video = document.getElementById('webcamFeed');
        const canvas = document.getElementById('webcamCanvas');
        const preview = document.getElementById('capturePreview');
        const capturedImg = document.getElementById('capturedImage');

        if (!video || !canvas) return;

        if (!stream || video.videoWidth === 0 || video.videoHeight === 0) {
            AppToast.error('Camera feed is not ready yet. Please try again in a moment.');
            return;
        }

        // Set canvas dimensions to match actual video feed size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw current frame onto canvas (un-mirroring natural selfie view)
        const ctx = canvas.getContext('2d');
        ctx.save();
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        ctx.restore();

        // Convert canvas image to JPEG blob/file
        canvas.toBlob((blob) => {
            if (!blob) {
                AppToast.error('Failed to capture photo from webcam feed.');
                return;
            }

            const file = new File([blob], `webcam_capture_${Date.now()}.jpg`, { type: 'image/jpeg' });

            // Display captured preview
            if (preview && capturedImg) {
                capturedImg.src = URL.createObjectURL(blob);
                preview.classList.remove('d-none');
            }

            // Pass file to Upload module
            if (typeof Upload !== 'undefined') {
                Upload.setFile(file);
            }

            AppToast.success('Photo captured! Click "Analyze Face Geometry" below.');
        }, 'image/jpeg', 0.95);
    }

    /**
     * Retake photo - resets capture preview and reactivates feed if needed.
     */
    function retake() {
        const preview = document.getElementById('capturePreview');
        if (preview) preview.classList.add('d-none');

        if (typeof Upload !== 'undefined') {
            Upload.clearFile();
        }

        if (!stream) {
            start();
        } else {
            AppToast.info('Ready for retake. Click the camera button to capture.');
        }
    }

    /**
     * Stop the webcam feed and release hardware resources.
     */
    function stop() {
        if (stream) {
            stream.getTracks().forEach(track => {
                track.stop();
            });
            stream = null;
        }

        const video = document.getElementById('webcamFeed');
        const startBtn = document.getElementById('startWebcamBtn');
        const captureBtn = document.getElementById('captureBtn');
        const stopBtn = document.getElementById('stopWebcamBtn');
        const badge = document.getElementById('cameraActiveBadge');

        if (video) {
            video.srcObject = null;
        }

        if (startBtn) startBtn.classList.remove('d-none');
        if (captureBtn) {
            captureBtn.classList.add('d-none');
            captureBtn.classList.remove('d-flex');
        }
        if (stopBtn) stopBtn.classList.add('d-none');
        if (badge) badge.classList.add('d-none');
    }

    return { start, capture, retake, stop, isSupported };
})();

