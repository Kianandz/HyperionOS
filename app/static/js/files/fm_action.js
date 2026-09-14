function promptCreateFolder(currentPath) {
    SwalDark.fire({
        title: 'New Folder',
        input: 'text',
        inputPlaceholder: 'Folder name...',
        showCancelButton: true,
        confirmButtonText: 'Create'
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
        title: 'New File',
        input: 'text',
        inputPlaceholder: 'e.g., index.html',
        showCancelButton: true,
        confirmButtonText: 'Create'
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
        title: 'Rename',
        input: 'text',
        inputValue: oldName,
        showCancelButton: true,
        confirmButtonText: 'Save'
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
        title: 'Delete Item',
        text: `Permanently delete [${name}]?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        confirmButtonText: 'Yes, Delete'
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
        title: 'Extract Archive',
        text: 'Extract archive contents to the current folder?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Extract'
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.getElementById('singleExtractForm');
            form.elements['path'].value = path;
            form.submit();
        }
    });
}