// Enterprise AI Forgery Detector - Frontend JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const previewDimensions = document.getElementById('previewDimensions');
    const btnRemovePreview = document.getElementById('btnRemovePreview');
    const analyzeForm = document.getElementById('analyzeForm');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const btnUploadMode = document.getElementById('btnUploadMode');
    const btnCameraMode = document.getElementById('btnCameraMode');
    const btnLoadUrl = document.getElementById('btnLoadUrl');
    const sampleButtons = document.querySelectorAll('.btn-sample');
    
    // Webcam modal elements
    const webcamModal = document.getElementById('webcamModal');
    const webcamVideo = document.getElementById('webcamVideo');
    const btnCapture = document.getElementById('btnCapture');
    const btnCloseWebcam = document.getElementById('btnCloseWebcam');
    const webcamImageInput = document.getElementById('webcamImageInput');
    let videoStream = null;

    // URL Modal elements
    const urlModal = document.getElementById('urlModal');
    const urlInput = document.getElementById('urlInput');
    const btnSubmitUrl = document.getElementById('btnSubmitUrl');
    const btnCloseUrl = document.getElementById('btnCloseUrl');
    const imageUrlInput = document.getElementById('imageUrlInput');
    const sampleNameInput = document.getElementById('sampleNameInput');

    // Visualizer toggles
    const vizToggles = document.querySelectorAll('.btn-viz-toggle');
    const vizDisplayArea = document.getElementById('vizDisplayArea');

    // Tabs
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    // 1. File Upload & Dropzone
    if (dropzone && fileInput) {
        dropzone.addEventListener('click', () => fileInput.click());

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            });
        });

        dropzone.addEventListener('drop', (e) => {
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files[0]) {
                handleFileSelect(fileInput.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        if (!file.type.match('image.*')) {
            alert('Please select an image file (PNG, JPG, WEBP).');
            return;
        }

        // Clear other inputs
        if (webcamImageInput) webcamImageInput.value = '';
        if (imageUrlInput) imageUrlInput.value = '';
        if (sampleNameInput) sampleNameInput.value = '';

        const reader = new FileReader();
        reader.onload = (e) => {
            showImagePreview(e.target.result, file.name);
        };
        reader.readAsDataURL(file);
    }

    function showImagePreview(src, name) {
        previewImage.src = src;
        previewContainer.style.display = 'flex';
        dropzone.style.display = 'none';
        btnAnalyze.disabled = false;
        btnAnalyze.style.opacity = '1';

        // Read dimensions
        const img = new Image();
        img.onload = () => {
            previewDimensions.textContent = `${name || 'Selected'} • ${img.naturalWidth} x ${img.naturalHeight} px`;
        };
        img.src = src;
    }

    // 2. Remove Preview / Reset
    if (btnRemovePreview) {
        btnRemovePreview.addEventListener('click', (e) => {
            e.stopPropagation();
            resetUploadState();
        });
    }

    function resetUploadState() {
        if (fileInput) fileInput.value = '';
        if (webcamImageInput) webcamImageInput.value = '';
        if (imageUrlInput) imageUrlInput.value = '';
        if (sampleNameInput) sampleNameInput.value = '';
        if (previewImage) previewImage.src = '';
        if (previewContainer) previewContainer.style.display = 'none';
        if (dropzone) dropzone.style.display = 'block';
        if (btnAnalyze) {
            btnAnalyze.disabled = true;
            btnAnalyze.style.opacity = '0.6';
        }
    }

    // 3. Built-in Samples Quick Ingestion
    sampleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleFile = btn.dataset.sample;
            if (!sampleFile) return;

            resetUploadState();
            sampleNameInput.value = sampleFile;
            const sampleUrl = `/static/samples/${sampleFile}`;
            showImagePreview(sampleUrl, sampleFile);
        });
    });

    // 4. Webcam Capture Modal
    if (btnCameraMode && webcamModal) {
        btnCameraMode.addEventListener('click', async () => {
            try {
                videoStream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
                webcamVideo.srcObject = videoStream;
                webcamModal.style.display = 'flex';
            } catch (err) {
                alert('Could not access camera: ' + err.message);
            }
        });

        btnCloseWebcam.addEventListener('click', closeWebcamModal);

        btnCapture.addEventListener('click', () => {
            const canvas = document.createElement('canvas');
            canvas.width = webcamVideo.videoWidth || 640;
            canvas.height = webcamVideo.videoHeight || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
            const dataUrl = canvas.toDataURL('image/jpeg', 0.95);

            closeWebcamModal();
            resetUploadState();
            webcamImageInput.value = dataUrl;
            showImagePreview(dataUrl, 'webcam_capture.jpg');
        });
    }

    function closeWebcamModal() {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
        }
        if (webcamModal) webcamModal.style.display = 'none';
    }

    // 5. URL Load Modal
    if (btnLoadUrl && urlModal) {
        btnLoadUrl.addEventListener('click', () => {
            urlModal.style.display = 'flex';
            urlInput.focus();
        });

        btnCloseUrl.addEventListener('click', () => {
            urlModal.style.display = 'none';
        });

        btnSubmitUrl.addEventListener('click', () => {
            const url = urlInput.value.trim();
            if (!url) return;
            resetUploadState();
            imageUrlInput.value = url;
            urlModal.style.display = 'none';
            showImagePreview(url, 'URL Ingest');
        });
    }

    // 6. Visualizer Display Toggle (Dual View, Original, ELA)
    vizToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            vizToggles.forEach(t => t.classList.remove('active'));
            toggle.classList.add('active');

            const mode = toggle.dataset.viz;
            const paneOriginal = document.getElementById('paneOriginal');
            const paneEla = document.getElementById('paneEla');

            if (!paneOriginal || !paneEla) return;

            if (mode === 'dual') {
                vizDisplayArea.style.gridTemplateColumns = '1fr 1fr';
                paneOriginal.style.display = 'flex';
                paneEla.style.display = 'flex';
            } else if (mode === 'original') {
                vizDisplayArea.style.gridTemplateColumns = '1fr';
                paneOriginal.style.display = 'flex';
                paneEla.style.display = 'none';
            } else if (mode === 'ela') {
                vizDisplayArea.style.gridTemplateColumns = '1fr';
                paneOriginal.style.display = 'none';
                paneEla.style.display = 'flex';
            }
        });
    });

    // 7. Interactive Tabs Switcher
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetId = btn.dataset.tab;
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });

    // 8. Form Submission Animation
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', () => {
            btnAnalyze.disabled = true;
            btnAnalyze.innerHTML = `
                <svg class="animate-spin" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                    <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
                </svg>
                Running CNN Forensic Analysis...
            `;
        });
    }
});
