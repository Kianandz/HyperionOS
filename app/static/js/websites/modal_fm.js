let currentFMDomain = '';
    let currentSubPath = ''; 
    let clipboard = null; 

    async function openFileManager(domain) {
        currentFMDomain = domain; currentSubPath = ''; 
        updatePathHeader(); openModal('modalFileManager'); await loadFiles();
    }

    function updatePathHeader() {
        document.getElementById('fmCurrentPath').innerText = `/${currentFMDomain}${currentSubPath ? '/' + currentSubPath : ''}`;
    }

    async function loadFiles() {
        const listEl = document.getElementById('fmFileList');
        listEl.innerHTML = '<tr><td colspan="3" class="p-4 text-center text-slate-500"><i class="fa fa-spinner fa-spin mr-2"></i>Loading files...</td></tr>';
        
        try {
            const res = await fetch(`/websites/files/list/${currentFMDomain}?subpath=${encodeURIComponent(currentSubPath)}`);
            const data = await res.json();
            
            let html = currentSubPath !== '' ? `<tr class="hover:bg-slate-800/80 transition cursor-pointer bg-slate-800/30" onclick="goUpFolder()"><td colspan="3" class="p-3 pl-4 text-slate-300 font-bold"><i class="fa fa-level-up-alt text-cyan-400 mr-2"></i> .. (Kembali)</td></tr>` : '';

            if (data.files.length === 0) {
                html += '<tr><td colspan="3" class="p-4 text-center text-slate-500">Folder kosong.</td></tr>';
            } else {
                html += data.files.map(f => {
                    const relativePath = currentSubPath ? `${currentSubPath}/${f.name}` : f.name;
                    return `<tr class="hover:bg-slate-800/50 transition">
                        <td data-label="${f.is_dir ? 'Folder' : 'File'}" class="p-3 pl-4 text-slate-200 ${f.is_dir ? 'cursor-pointer hover:text-cyan-400 font-medium' : ''}" ${f.is_dir ? `onclick="enterFolder('${f.name}')"` : ''}>
                            <i class="fa ${f.is_dir ? 'fa-folder text-amber-400' : 'fa-file text-slate-400'} mr-2"></i> ${f.name}
                        </td>
                        <td data-label="${f.is_dir ? '-' : "Size"}" class="p-3 text-xs">${f.is_dir ? '-' : (f.size / 1024).toFixed(2) + ' KB'}</td>
                        <td data-label="Action" class="p-3 pr-4 text-right space-x-1.5">
                            ${!f.is_dir ? `<button onclick="openEditor('${relativePath}')" class="px-2 py-1 bg-amber-600/20 text-amber-400 hover:bg-amber-600 hover:text-white rounded text-xs"><i class="fa fa-edit"></i></button>` : ''}
                            <button onclick="setClipboard('copy', '${relativePath}', '${f.name}')" class="px-2 py-1 bg-slate-700 text-slate-300 hover:bg-slate-600 rounded text-xs"><i class="fa fa-copy"></i></button>
                            <button onclick="setClipboard('move', '${relativePath}', '${f.name}')" class="px-2 py-1 bg-slate-700 text-slate-300 hover:bg-slate-600 rounded text-xs"><i class="fa fa-cut"></i></button>
                            <button onclick="changeChmod('${relativePath}')" class="px-2 py-1 bg-slate-700 text-slate-300 hover:bg-slate-600 rounded text-xs"><i class="fa fa-key"></i></button>
                            ${!f.is_dir ? `<a href="/websites/files/download/${currentFMDomain}/${relativePath}" target="_blank" class="px-2 py-1 bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600 hover:text-white rounded text-xs inline-block"><i class="fa fa-download"></i></a>` : ''}
                            <button onclick="deleteFile('${relativePath}')" class="px-2 py-1 bg-rose-600/20 text-rose-400 hover:bg-rose-600 hover:text-white rounded text-xs"><i class="fa fa-trash"></i></button>
                        </td>
                    </tr>`;
                }).join('');
            }
            listEl.innerHTML = html; updatePathHeader();
        } catch (e) {
            listEl.innerHTML = '<tr><td colspan="3" class="p-4 text-center text-rose-500">Error load file.</td></tr>';
        }
    }

    function enterFolder(folderName) { currentSubPath = currentSubPath ? `${currentSubPath}/${folderName}` : folderName; loadFiles(); }
    function goUpFolder() { if (!currentSubPath) return; let parts = currentSubPath.split('/'); parts.pop(); currentSubPath = parts.join('/'); loadFiles(); }

    async function handleUpload(files) {
        if (!files.length) return;
        const formData = new FormData(); formData.append("subpath", currentSubPath);
        for (let i = 0; i < files.length; i++) formData.append("files", files[i], files[i].webkitRelativePath || files[i].name);
        
        document.getElementById('fmUploadStatus').classList.remove('hidden');
        try {
            await fetch(`/websites/files/upload/${currentFMDomain}`, { method: 'POST', body: formData });
            await loadFiles();
        } catch(e) {
            Swal.fire({ title: 'Upload Failed', text: e, icon: 'error', background: '#0f172a', color: '#fff' });
        } finally {
            document.getElementById('fmUploadStatus').classList.add('hidden');
        }
    }

    async function createItem(type) {
        const { value: name } = await Swal.fire({ title: `New ${type} :`, input: 'text', showCancelButton: true, background: '#0f172a', color: '#fff' });
        if (!name) return;
        const form = new FormData(); form.append('name', name); form.append('type', type); form.append('subpath', currentSubPath);
        await fetch(`/websites/files/create/${currentFMDomain}`, { method: 'POST', body: form }); await loadFiles();
    }

    function setClipboard(action, relativePath, name) {
        clipboard = { action, targetPath: relativePath, name };
        document.getElementById('fmPasteBtn').classList.remove('hidden');
        document.getElementById('fmPasteBtn').innerHTML = `<i class="fa fa-paste mr-1"></i> Paste (${name})`;
    }

    async function executePaste() {
        if (!clipboard) return;
        const { value: newName, isConfirmed } = await Swal.fire({ title: "Rename paste", input: 'text', inputValue: clipboard.name, text: "(Skip if exists)", showCancelButton: true, background: '#0f172a', color: '#fff' });
        if (!isConfirmed) return;
        const destPath = currentSubPath ? `${currentSubPath}/${newName || clipboard.name}` : (newName || clipboard.name);
        const form = new FormData(); form.append('action', clipboard.action); form.append('target', clipboard.targetPath); form.append('dest', destPath);
        await fetch(`/websites/files/action/${currentFMDomain}`, { method: 'POST', body: form });
        clipboard = null; document.getElementById('fmPasteBtn').classList.add('hidden'); await loadFiles();
    }

    async function changeChmod(relativePath) {
        const { value: mods } = await Swal.fire({ title: "Set Permission", input: 'text', inputValue: "755", showCancelButton: true, background: '#0f172a', color: '#fff' });
        if (!mods) return;
        const form = new FormData(); form.append('action', 'chmod'); form.append('target', relativePath); form.append('mods', mods);
        await fetch(`/websites/files/action/${currentFMDomain}`, { method: 'POST', body: form });
    }

    async function openEditor(relativePath) {
        const res = await fetch(`/websites/files/read/${currentFMDomain}/${relativePath}`); const data = await res.json();
        document.getElementById('editorFilename').innerText = relativePath;
        document.getElementById('editorTextarea').value = data.content || '';
        openModal('modalEditor');
    }

    async function saveFileContent() {
        const relativePath = document.getElementById('editorFilename').innerText;
        const form = new FormData(); form.append('content', document.getElementById('editorTextarea').value);
        await fetch(`/websites/files/write/${currentFMDomain}/${relativePath}`, { method: 'POST', body: form });
        closeModal('modalEditor');
    }

    async function deleteFile(relativePath) {
        const res = await Swal.fire({ title: `Delete ${relativePath}?`, icon: 'warning', showCancelButton: true, confirmButtonColor: '#e11d48', background: '#0f172a', color: '#fff' });
        if (!res.isConfirmed) return;
        await fetch(`/websites/files/delete/${currentFMDomain}/${relativePath}`, { method: 'POST' }); await loadFiles();
    }