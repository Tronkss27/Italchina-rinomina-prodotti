// JavaScript per Image Renamer Web App
document.addEventListener('DOMContentLoaded', function() {
    
    // Elementi del DOM
    const uploadForm = document.getElementById('uploadForm');
    const mappingFile = document.getElementById('mappingFile');
    const imageFiles = document.getElementById('imageFiles');
    const folderInput = document.getElementById('folderInput');
    const mappingPreview = document.getElementById('mappingPreview');
    const imagesPreview = document.getElementById('imagesPreview');
    const processBtn = document.getElementById('processBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');
    const downloadSection = document.getElementById('downloadSection');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorSection = document.getElementById('errorSection');
    const errorContent = document.getElementById('errorContent');

    // Variable to store all selected images
    let selectedImages = [];

    // Event listeners per le anteprime dei file
    mappingFile.addEventListener('change', function() {
        updateFilePreview(this, mappingPreview, 'mapping');
    });

    imageFiles.addEventListener('change', function() {
        selectedImages = Array.from(this.files);
        updateImagesPreview();
        updateUploadState('files');
    });

    folderInput.addEventListener('change', function() {
        // Filter only image files from folder
        const imageExtensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif'];
        selectedImages = Array.from(this.files).filter(file => {
            const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
            return imageExtensions.includes(ext);
        });
        updateImagesPreview();
        updateUploadState('folder');
    });

    // Event listener per il form
    uploadForm.addEventListener('submit', handleFormSubmit);

    // Event listener per il download
    downloadBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/download';
    });

    /**
     * Aggiorna l'anteprima dei file selezionati
     */
    function updateFilePreview(input, previewElement, type) {
        const files = input.files;
        
        if (files.length === 0) {
            previewElement.innerHTML = '';
            previewElement.classList.remove('has-files');
            return;
        }

        previewElement.classList.add('has-files');

        if (type === 'mapping') {
            const file = files[0];
            previewElement.innerHTML = `
                <strong>File selezionato:</strong> ${file.name} 
                (${formatFileSize(file.size)})
            `;
        } else if (type === 'images') {
            previewElement.innerHTML = `
                <strong>Immagini selezionate:</strong> ${files.length} file
                <br><small>${Array.from(files).map(f => f.name).join(', ')}</small>
            `;
        }
    }

    /**
     * Formatta la dimensione del file in modo leggibile
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Gestisce l'invio del form
     */
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        // Nascondi sezioni precedenti
        hideAllSections();
        
        // Verifica che i file siano stati selezionati
        if (!mappingFile.files[0] || selectedImages.length === 0) {
            showError('Seleziona sia il file di mapping che le immagini (file singoli o cartella).');
            return;
        }

        // Mostra loading
        showLoading();
        
        // Disabilita il pulsante
        processBtn.disabled = true;
        processBtn.textContent = 'Elaborazione in corso...';

        try {
            // Prepara i dati per l'upload
            const formData = new FormData();
            formData.append('mapping_file', mappingFile.files[0]);
            
            // Aggiungi tutte le immagini selezionate
            selectedImages.forEach(file => {
                formData.append('images', file);
            });

            // Invia la richiesta
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showResults(result);
            } else {
                showError(result.error || 'Errore sconosciuto durante il processamento.');
            }

        } catch (error) {
            console.error('Errore:', error);
            showError('Errore di connessione. Riprova più tardi.');
        } finally {
            // Ripristina il pulsante
            processBtn.disabled = false;
            processBtn.textContent = 'Avvia Rinominazione';
            hideLoading();
        }
    }

    /**
     * Mostra la sezione di loading
     */
    function showLoading() {
        loadingSpinner.style.display = 'block';
    }

    /**
     * Nasconde la sezione di loading
     */
    function hideLoading() {
        loadingSpinner.style.display = 'none';
    }

    /**
     * Mostra i risultati del processamento
     */
    function showResults(result) {
        const stats = result.stats;
        
        resultsContent.innerHTML = `
            <p class="success"><strong>${result.message}</strong></p>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">${stats.processed}</div>
                    <div class="stat-label">File Rinominati</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${stats.skipped}</div>
                    <div class="stat-label">File Saltati</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${stats.errors}</div>
                    <div class="stat-label">Errori</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${stats.total_uploaded}</div>
                    <div class="stat-label">File Caricati</div>
                </div>
            </div>
        `;

        // Mostra il pulsante di download se ci sono file processati
        if (stats.processed > 0) {
            downloadSection.style.display = 'block';
            downloadBtn.href = result.download_url;
        }

        resultsSection.style.display = 'block';
        
        // Scroll ai risultati
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Mostra un errore
     */
    function showError(message) {
        errorContent.innerHTML = `<p>${message}</p>`;
        errorSection.style.display = 'block';
        
        // Scroll all'errore
        errorSection.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Nasconde tutte le sezioni di risultato
     */
    function hideAllSections() {
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
        downloadSection.style.display = 'none';
    }

    /**
     * Gestisce il drag & drop per i file
     */
    function setupDragAndDrop() {
        const fileInputs = [mappingFile, imageFiles];
        
        fileInputs.forEach(input => {
            const parent = input.parentElement;
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                parent.addEventListener(eventName, preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                parent.addEventListener(eventName, highlight, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                parent.addEventListener(eventName, unhighlight, false);
            });

            parent.addEventListener('drop', handleDrop, false);

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            function highlight(e) {
                parent.classList.add('dragover');
            }

            function unhighlight(e) {
                parent.classList.remove('dragover');
            }

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                input.files = files;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            }
        });
    }

    // Inizializza drag & drop
    setupDragAndDrop();

    /**
     * Mostra informazioni aggiuntive al caricamento della pagina
     */
    function showWelcomeInfo() {
        console.log('Image Renamer Web App caricata!');
        console.log('Per supporto, consulta la documentazione nella sezione "Guida all\'uso"');
    }

    // Mostra info di benvenuto
    showWelcomeInfo();

    /**
     * Aggiorna l'anteprima delle immagini selezionate (da file o cartella)
     */
    function updateImagesPreview() {
        if (selectedImages.length === 0) {
            imagesPreview.innerHTML = '';
            imagesPreview.classList.remove('has-files');
            return;
        }

        imagesPreview.classList.add('has-files');
        
        const totalSize = selectedImages.reduce((sum, file) => sum + file.size, 0);
        const folderPaths = [...new Set(selectedImages.map(f => f.webkitRelativePath || f.name).map(path => path.split('/')[0]))];
        
        let pathInfo = '';
        if (selectedImages[0].webkitRelativePath) {
            pathInfo = folderPaths.length > 1 ? 
                `<br><small>Da ${folderPaths.length} cartelle: ${folderPaths.join(', ')}</small>` :
                `<br><small>Dalla cartella: ${folderPaths[0]}</small>`;
        }

        imagesPreview.innerHTML = `
            <strong>Immagini selezionate:</strong> ${selectedImages.length} file
            (${formatFileSize(totalSize)})
            ${pathInfo}
            <br><small>File: ${selectedImages.slice(0, 5).map(f => f.name).join(', ')}${selectedImages.length > 5 ? '...' : ''}</small>
        `;
    }

    /**
     * Aggiorna lo stato visivo dei pulsanti di upload
     */
    function updateUploadState(activeType) {
        const fileOption = document.querySelector('.upload-option:has(#imageFiles)');
        const folderOption = document.querySelector('.upload-option:has(#folderInput)');
        
        // Reset states
        fileOption.classList.remove('has-files');
        folderOption.classList.remove('has-files');
        
        // Set active state
        if (activeType === 'files') {
            fileOption.classList.add('has-files');
            // Clear folder input
            folderInput.value = '';
        } else if (activeType === 'folder') {
            folderOption.classList.add('has-files');
            // Clear file input
            imageFiles.value = '';
        }
    }
}); 