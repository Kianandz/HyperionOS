// Config SweetAlert2 (Main Theme)
const SwalDark = Swal.mixin({
    background: '#0f172a',
    color: '#f8fafc',
    confirmButtonColor: '#4f46e5',
    cancelButtonColor: '#334155',
    customClass: {
        popup: 'border border-slate-700 rounded-2xl shadow-2xl',
        confirmButton: 'rounded-lg px-5 py-2 font-semibold',
        cancelButton: 'rounded-lg px-5 py-2 font-medium'
    }
});

// Config Toast Notification 
const ToastDark = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 2500,
    timerProgressBar: true,
    background: '#1e293b',
    color: '#f8fafc',
    customClass: { popup: 'border border-slate-700/50 rounded-xl shadow-xl' }
});

// --- DROPDOWN LOGIC ---
function toggleDropdown(id) {
    const dropdown = document.getElementById(id);
    if (dropdown.classList.contains('hidden')) {
        // Hide others first
        document.querySelectorAll('.dropdown-container > div:not(.hidden)').forEach(el => el.classList.add('hidden'));
        dropdown.classList.remove('hidden');
    } else {
        dropdown.classList.add('hidden');
    }
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.dropdown-container')) {
        document.querySelectorAll('.dropdown-container > div:not(.hidden)').forEach(dropdown => {
            dropdown.classList.add('hidden');
        });
    }
});

// --- CLIPBOARD SYSTEM ---
function setClipboard(path, name, action) {
    const item = { path: path, name: name, action: action };
    localStorage.setItem('fm_clipboard', JSON.stringify(item));
    checkClipboard();
    
    ToastDark.fire({
        icon: 'success',
        title: `Disimpan ke Clipboard (${action.toUpperCase()})`
    });
}

function clearClipboard() {
    localStorage.removeItem('fm_clipboard');
    checkClipboard();
}

function checkClipboard() {
    const raw = localStorage.getItem('fm_clipboard');
    const pasteBar = document.getElementById('pasteBar');
    const clipboardText = document.getElementById('clipboardText');
    const pasteSrcInput = document.getElementById('pasteSrcInput');
    const pasteActionInput = document.getElementById('pasteActionInput');

    if (raw && pasteBar) {
        try {
            const item = JSON.parse(raw);
            // FIX: Paksa selalu jadi Array, baik single item maupun batch
            const pathsArray = Array.isArray(item.path) ? item.path : [item.path];
            const label = pathsArray.length > 1 ? `${pathsArray.length} items` : (item.name || pathsArray[0]);

            if (clipboardText) clipboardText.textContent = `[${item.action.toUpperCase()}] ${label}`;
            // Kirim JSON Array yang valid (e.g. ["path/file.txt"])
            if (pasteSrcInput) pasteSrcInput.value = JSON.stringify(pathsArray);
            if (pasteActionInput) pasteActionInput.value = item.action;
            pasteBar.classList.remove('hidden');
        } catch (e) {
            clearClipboard();
        }
    } else if (pasteBar) {
        pasteBar.classList.add('hidden');
    }
}

function handlePasteSubmit(event) {
    // Biar form-nya tetep ke-submit ke backend
    event.preventDefault();
    
    // Bersihin localStorage clipboard
    localStorage.removeItem('fm_clipboard');
    
    // Sembunyikan bar-nya seketika
    const pasteBar = document.getElementById('pasteBar');
    if (pasteBar) {
        pasteBar.classList.add('hidden');
    }
    
    // Submit form secara manual setelah clipboard dibersihkan
    event.target.submit();
}

// --- SELECTION & FLOATING BATCH BAR ---
function toggleSelectAll(masterCheckbox) {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    checkboxes.forEach(cb => cb.checked = masterCheckbox.checked);
    updateBatchBar();
}

function clearSelection() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    checkboxes.forEach(cb => cb.checked = false);
    const masterCb = document.getElementById('selectAll');
    if (masterCb) masterCb.checked = false;
    updateBatchBar();
}

function updateBatchBar() {
    const selected = document.querySelectorAll('.file-checkbox:checked');
    const batchBar = document.getElementById('batchActionBar');
    const selectedCount = document.getElementById('selectedCount');

    if (selected.length > 0) {
        if (selectedCount) selectedCount.textContent = selected.length;
        if (batchBar) {
            batchBar.classList.remove('pointer-events-none');
            // Animate In (Slide up)
            setTimeout(() => {
                batchBar.classList.remove('translate-y-[150%]', 'opacity-0');
            }, 10);
        }
    } else {
        if (batchBar) {
            // Animate Out (Slide down)
            batchBar.classList.add('translate-y-[150%]', 'opacity-0');
            batchBar.classList.add('pointer-events-none');
        }
        const masterCb = document.getElementById('selectAll');
        if (masterCb) masterCb.checked = false;
    }
}

function getSelectedPaths() {
    const selected = document.querySelectorAll('.file-checkbox:checked');
    return Array.from(selected).map(cb => cb.getAttribute('data-path'));
}

// Batch Actions
function batchDelete() {
    const paths = getSelectedPaths();
    if (paths.length === 0) return;

    SwalDark.fire({
        title: 'Hapus Item Terpilih?',
        text: `Anda yakin ingin menghapus ${paths.length} item secara permanen?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        confirmButtonText: 'Ya, Hapus',
        cancelButtonText: 'Batal'
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.getElementById('batchDeleteForm');
            document.getElementById('batchDeletePaths').value = JSON.stringify(paths);
            form.submit();
        }
    });
}

function batchCompress() {
    const paths = getSelectedPaths();
    if (paths.length === 0) return;

    SwalDark.fire({
        title: 'Kompres ke ZIP',
        input: 'text',
        inputValue: 'archive.zip',
        inputPlaceholder: 'nama_file.zip',
        showCancelButton: true,
        confirmButtonText: 'Kompres'
    }).then((result) => {
        if (result.isConfirmed && result.value) {
            const form = document.getElementById('batchCompressForm');
            document.getElementById('batchCompressPaths').value = JSON.stringify(paths);
            
            let val = result.value;
            if(!val.toLowerCase().endsWith('.zip')) val += '.zip';
            
            document.getElementById('batchCompressName').value = val;
            form.submit();
        }
    });
}

function batchCopyCut(action) {
    const paths = getSelectedPaths();
    if (paths.length === 0) return;
    
    setClipboard(paths, `${paths.length} items`, action);
    clearSelection(); // Biar rapih, bar ilang setelah dicopy
}

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

// --- SINGLE PROMPTS ---
function promptCreateFolder(currentPath) {
    SwalDark.fire({
        title: 'Folder Baru',
        input: 'text',
        inputPlaceholder: 'Nama folder...',
        showCancelButton: true,
        confirmButtonText: 'Buat'
    }).then((result) => {
        if (result.isConfirmed && result.value) {
            const form = document.getElementById('createFolderForm');
            form.elements['folder_name'].value = result.value;
            form.submit();
        }
    });
}

function promptCreateFile(currentPath) {
    SwalDark.fire({
        title: 'File Baru',
        input: 'text',
        inputPlaceholder: 'contoh: index.html',
        showCancelButton: true,
        confirmButtonText: 'Buat'
    }).then((result) => {
        if (result.isConfirmed && result.value) {
            const form = document.getElementById('createFileForm');
            form.elements['file_name'].value = result.value;
            form.submit();
        }
    });
}

function promptRename(path, oldName) {
    SwalDark.fire({
        title: 'Ganti Nama',
        input: 'text',
        inputValue: oldName,
        showCancelButton: true,
        confirmButtonText: 'Simpan'
    }).then((result) => {
        if (result.isConfirmed && result.value && result.value !== oldName) {
            const form = document.getElementById('singleRenameForm');
            form.elements['path'].value = path;
            form.elements['new_name'].value = result.value;
            form.submit();
        }
    });
}

function promptDelete(path, name) {
    SwalDark.fire({
        title: 'Hapus Item',
        text: `Hapus [${name}] secara permanen?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        confirmButtonText: 'Ya, Hapus'
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.getElementById('singleDeleteForm');
            form.elements['path'].value = path;
            form.submit();
        }
    });
}

function promptExtract(path) {
    SwalDark.fire({
        title: 'Ekstrak Arsip',
        text: 'Ekstrak isi arsip ini ke folder saat ini?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Ekstrak'
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.getElementById('singleExtractForm');
            form.elements['path'].value = path;
            form.submit();
        }
    });
}

// --- SEARCH & SORT ---
function searchTable() {
    const input = document.getElementById("searchInput").value.toLowerCase();
    const rows = document.querySelectorAll("#fileTableBody tr");
    rows.forEach(row => {
        const nameCell = row.querySelector("td:nth-child(2)");
        if (nameCell) {
            const text = nameCell.textContent.toLowerCase();
            row.style.display = text.includes(input) ? "" : "none";
        }
    });
}

let sortDirection = false;
function sortTable(columnIndex, isNumber = false) {
    const tbody = document.getElementById("fileTableBody");
    const rows = Array.from(tbody.querySelectorAll("tr"));
    
    sortDirection = !sortDirection;

    rows.sort((a, b) => {
        const cellA = a.querySelectorAll("td")[columnIndex];
        const cellB = b.querySelectorAll("td")[columnIndex];
        if (!cellA || !cellB) return 0;

        const valA = cellA.getAttribute("data-sort-val") || cellA.textContent.trim();
        const valB = cellB.getAttribute("data-sort-val") || cellB.textContent.trim();

        if (isNumber) {
            return sortDirection ? parseFloat(valA) - parseFloat(valB) : parseFloat(valB) - parseFloat(valA);
        } else {
            return sortDirection ? valA.localeCompare(valB) : valB.localeCompare(valA);
        }
    });

    tbody.append(...rows);
}

// INIT
document.addEventListener('DOMContentLoaded', checkClipboard);