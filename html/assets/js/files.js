async function fetchFiles(path = "") {
    try {
        const res = await fetch(`${API_BASE}/files/list?path=${encodeURIComponent(path)}`);
        const data = await res.json();

        document.getElementById('fm-current-path').innerText = "/" + (data.current_path || "");
        const tbody = document.getElementById('file-manager-list');
        tbody.innerHTML = '';

        data.items.forEach(item => {
            const icon = item.is_dir ? 'fa-folder text-yellow-400' : 'fa-file text-slate-400';
            const size = item.is_dir ? '-' : `${(item.size_bytes / 1024).toFixed(1)} KB`;
            tbody.innerHTML += `
                <tr class="border-b border-slate-800/50 hover:bg-slate-800/20">
                    <td class="p-4 font-semibold text-white">
                        <i class="fa-solid ${icon} mr-2"></i> ${item.name}
                    </td>
                    <td class="p-4 text-xs text-slate-400">${item.is_dir ? 'Folder' : 'File'}</td>
                    <td class="p-4 text-xs font-mono text-slate-400">${size}</td>
                    <td class="p-4 text-right">
                        <button onclick="deleteFileItem('${item.path}')" class="text-rose-400 hover:text-rose-300"><i class="fa-solid fa-trash"></i></button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        console.error("Gagal load files:", err);
    }
}

async function deleteFileItem(path) {
    if (!confirm(`Hapus ${path}?`)) return;
    await fetch(`${API_BASE}/files/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path })
    });
    fetchFiles();
}

onTabChange('files', fetchFiles);