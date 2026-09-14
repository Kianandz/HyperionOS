function setClipboard(path, name, action) {
    const item = { path: path, name: name, action: action };
    localStorage.setItem('fm_clipboard', JSON.stringify(item));
    checkClipboard();
    
    ToastDark.fire({
        icon: 'success',
        title: `Saved to Clipboard (${action.toUpperCase()})`
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
            const pathsArray = Array.isArray(item.path) ? item.path : [item.path];
            const label = pathsArray.length > 1 ? `${pathsArray.length} items` : (item.name || pathsArray[0]);

            if (clipboardText) clipboardText.textContent = `[${item.action.toUpperCase()}] ${label}`;
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
    event.preventDefault();
    localStorage.removeItem('fm_clipboard');
    const pasteBar = document.getElementById('pasteBar');
    if (pasteBar) {
        pasteBar.classList.add('hidden');
    }
    event.target.submit();
}

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
            setTimeout(() => {
                batchBar.classList.remove('translate-y-[150%]', 'opacity-0');
            }, 10);
        }
    } else {
        if (batchBar) {
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

function batchDelete() {
    const paths = getSelectedPaths();
    if (paths.length === 0) return;

    SwalDark.fire({
        title: 'Delete Selected Items?',
        text: `Are you sure you want to permanently delete ${paths.length} items?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        confirmButtonText: 'Yes, Delete',
        cancelButtonText: 'Cancel'
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
        title: 'Compress to ZIP',
        input: 'text',
        inputValue: 'archive.zip',
        inputPlaceholder: 'filename.zip',
        showCancelButton: true,
        confirmButtonText: 'Compress'
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
    clearSelection();
}

document.addEventListener('DOMContentLoaded', checkClipboard);