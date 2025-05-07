// Initialize Uppy file uploader
function initializeUppy() {
    // Check if Uppy is loaded
    if (typeof Uppy === 'undefined') {
        console.error('Uppy is not loaded. Make sure to include the Uppy scripts and CSS.');
        return;
    }

    // Find the uppy container
    const uppyContainer = document.getElementById('uppy-container');
    if (!uppyContainer) {
        setTimeout(initializeUppy, 500);
        return;
    }

    // Create a new Uppy instance
    const uppy = new Uppy.Core({
        debug: true,
        autoProceed: false,
        restrictions: {
            maxFileSize: 10 * 1024 * 1024, // 10MB
            maxNumberOfFiles: 1,
            allowedFileTypes: ['.csv', '.xlsx', '.xls']
        }
    });

    // Add Dashboard plugin
    uppy.use(Uppy.Dashboard, {
        inline: true,
        target: uppyContainer,
        height: 300,
        width: '100%',
        showProgressDetails: true,
        proudlyDisplayPoweredByUppy: false,
        theme: document.documentElement.classList.contains('dark') ? 'dark' : 'light'
    });

    // Add file validation
    uppy.use(Uppy.Compressor);

    // Handle file upload
    uppy.on('file-added', (file) => {
        console.log('File added:', file.name);
        
        // Enable the process button
        const processBtn = document.getElementById('process_btn');
        if (processBtn) {
            processBtn.disabled = false;
        }
    });

    // Handle file removal
    uppy.on('file-removed', (file) => {
        console.log('File removed:', file.name);
        
        // Disable the process button if no files
        if (uppy.getFiles().length === 0) {
            const processBtn = document.getElementById('process_btn');
            if (processBtn) {
                processBtn.disabled = true;
            }
        }
    });

    // Handle upload success
    uppy.on('upload-success', (file, response) => {
        console.log('Upload success:', file.name, response);
    });

    // Handle upload error
    uppy.on('upload-error', (file, error, response) => {
        console.error('Upload error:', file.name, error, response);
        
        // Show error message
        const statusIndicator = document.getElementById('scada_status');
        if (statusIndicator) {
            statusIndicator.innerHTML = `<div class='error-message'><i class='fas fa-exclamation-circle'></i> Error uploading file: ${error}</div>`;
        }
    });

    // Handle process button click
    const processBtn = document.getElementById('process_btn');
    if (processBtn) {
        processBtn.addEventListener('click', () => {
            const files = uppy.getFiles();
            if (files.length === 0) {
                const statusIndicator = document.getElementById('scada_status');
                if (statusIndicator) {
                    statusIndicator.innerHTML = `<div class='warning-message'><i class='fas fa-exclamation-triangle'></i> Please upload a file first.</div>`;
                }
                return;
            }

            // Get the file data
            const file = files[0];
            
            // Create a FormData object
            const formData = new FormData();
            formData.append('file', file.data);
            
            // Show processing message
            const statusIndicator = document.getElementById('scada_status');
            if (statusIndicator) {
                statusIndicator.innerHTML = `<div class='info-message'><i class='fas fa-spinner fa-spin'></i> Processing file...</div>`;
            }
            
            // Submit the form
            const fileUploadForm = document.getElementById('file-upload-form');
            if (fileUploadForm) {
                fileUploadForm.submit();
            }
        });
        
        // Initially disable the process button
        processBtn.disabled = true;
    }

    // Update Uppy theme when the page theme changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                const isDark = document.documentElement.classList.contains('dark');
                const dashboard = document.querySelector('.uppy-Dashboard');
                if (dashboard) {
                    if (isDark) {
                        dashboard.classList.add('uppy-Dashboard--dark');
                    } else {
                        dashboard.classList.remove('uppy-Dashboard--dark');
                    }
                }
            }
        });
    });
    
    observer.observe(document.documentElement, { attributes: true });

    return uppy;
}

// Initialize Uppy when the page loads
document.addEventListener('DOMContentLoaded', initializeUppy);
// Also try to initialize when the page changes
setInterval(initializeUppy, 2000);
