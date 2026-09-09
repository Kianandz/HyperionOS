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