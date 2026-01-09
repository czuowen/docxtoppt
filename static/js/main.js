const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadContent = document.querySelector('.upload-content');
const processingUI = document.getElementById('processing-ui');
const successUI = document.getElementById('success-ui');
const downloadLink = document.getElementById('download-link');
const resultFilename = document.getElementById('result-filename');

// Drag and drop handlers
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', handleDrop, false);
fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length === 0) return;
    const file = files[0];

    if (!file.name.endsWith('.docx')) {
        alert('请上传 .docx 格式的文件');
        return;
    }

    startConversion(file);
}

async function startConversion(file) {
    // UI states
    uploadContent.classList.add('hidden');
    processingUI.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showSuccess(data);
        } else {
            alert('转换失败: ' + (data.error || '未知错误'));
            resetUI();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('转换过程中发生错误，请稍后重试');
        resetUI();
    }
}

function showSuccess(data) {
    processingUI.classList.add('hidden');
    successUI.classList.remove('hidden');

    downloadLink.href = data.download_url;
    downloadLink.download = data.filename;
    resultFilename.innerText = `已成功转换！`;
}

function resetUI() {
    successUI.classList.add('hidden');
    processingUI.classList.add('hidden');
    uploadContent.classList.remove('hidden');
    fileInput.value = '';
}
