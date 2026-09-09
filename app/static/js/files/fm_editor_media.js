// --- TEXT EDITOR ---
async function openTextEditor(path) {
    const modal = document.getElementById('fm-editor-modal');
    const title = document.getElementById('fm-editor-title');
    const textarea = document.getElementById('fm-editor-content');
    const pathInput = document.getElementById('fm-editor-path');

    if (title) title.innerHTML = `<i class="fa fa-solid fa-code mr-2"></i> Edit: /${path}`;
    if (pathInput) pathInput.value = path;
    if (textarea) textarea.value = "Memuat...";

    if (modal) modal.classList.remove('hidden');

    try {
        const response = await fetch(`/files/api/read-file?path=${encodeURIComponent(path)}`);
        const result = await response.json();
        if (result.status === 'success') {
            if (textarea) textarea.value = result.content;
        } else {
            SwalDark.fire('Gagal', result.message, 'error');
            closeTextEditor();
        }
    } catch (err) {
        SwalDark.fire('Error', 'Gagal memuat isi file.', 'error');
        closeTextEditor();
    }
}

function closeTextEditor() {
    const modal = document.getElementById('fm-editor-modal');
    if (modal) modal.classList.add('hidden');
}

async function saveTextContent() {
    const path = document.getElementById('fm-editor-path').value;
    const content = document.getElementById('fm-editor-content').value;

    const formData = new FormData();
    formData.append('path', path);
    formData.append('content', content);

    try {
        const response = await fetch('/files/api/write-file', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.status === 'success') {
            ToastDark.fire({ icon: 'success', title: 'Perubahan Disimpan!' });
            closeTextEditor();
        } else {
            SwalDark.fire('Gagal', result.message, 'error');
        }
    } catch (err) {
        SwalDark.fire('Error', 'Gagal menyimpan.', 'error');
    }
}

// --- MEDIA PREVIEWS ---
function openImagePreview(path, name) {
    const modal = document.getElementById('fm-image-modal');
    const title = document.getElementById('fm-image-title');
    const img = document.getElementById('fm-image-preview');

    if (title) title.textContent = name;
    if (img) img.src = `/files/download?path=${encodeURIComponent(path)}`;
    if (modal) modal.classList.remove('hidden');
}

function closeImagePreview() {
    const modal = document.getElementById('fm-image-modal');
    const img = document.getElementById('fm-image-preview');
    if (modal) modal.classList.add('hidden');
    if (img) img.src = '';
}

function openVideoPreview(path, name) {
    const modal = document.getElementById('fm-video-modal');
    const title = document.getElementById('fm-video-title');
    const player = document.getElementById('fm-video-preview');

    if (title) title.textContent = name;
    if (player) player.src = `/files/download?path=${encodeURIComponent(path)}`;
    if (modal) modal.classList.remove('hidden');
}

function closeVideoPreview() {
    const modal = document.getElementById('fm-video-modal');
    const player = document.getElementById('fm-video-preview');
    if (player) {
        player.pause();
        player.src = '';
    }
    if (modal) modal.classList.add('hidden');
}

function handleItemClick(path, name, isDir) {
    if (isDir) return;
    const lower = name.toLowerCase();
    if (lower.endsWith('.jpg') || lower.endsWith('.png') || lower.endsWith('.jpeg') || lower.endsWith('.webp') || lower.endsWith('.gif')) {
        openImagePreview(path, name);
    } else if (lower.endsWith('.mp4') || lower.endsWith('.webm') || lower.endsWith('.mkv')) {
        openVideoPreview(path, name);
    } else if (lower.endsWith('.zip') || lower.endsWith('.tar.gz') || lower.endsWith('.gz')) {
        promptExtract(path);
    } else {
        openTextEditor(path);
    }
}