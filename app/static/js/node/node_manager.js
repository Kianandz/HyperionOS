document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
});

async function fetchStatus() {
    try {
        const res = await fetch('/websites/node/api/status');
        const data = await res.json();
        renderDependencies(data.deps);
        renderProjects(data.projects);
    } catch (e) {
        console.error("Gagal memuat status node", e);
    }
}

function renderDependencies(deps) {
    const grid = document.getElementById('dep-status-grid');
    const actionArea = document.getElementById('dep-action-area');
    
    const isAllInstalled = deps.node && deps.npm && deps.pm2;

    grid.innerHTML = `
        <div class="p-4 bg-slate-800/40 rounded-xl border border-slate-800 flex items-center justify-between">
            <span>Node.js</span>
            <span class="px-2.5 py-1 rounded-lg text-xs font-bold ${deps.node ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">${deps.node ? 'Installed' : 'Missing'}</span>
        </div>
        <div class="p-4 bg-slate-800/40 rounded-xl border border-slate-800 flex items-center justify-between">
            <span>NPM</span>
            <span class="px-2.5 py-1 rounded-lg text-xs font-bold ${deps.npm ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">${deps.npm ? 'Installed' : 'Missing'}</span>
        </div>
        <div class="p-4 bg-slate-800/40 rounded-xl border border-slate-800 flex items-center justify-between">
            <span>PM2 (Manager: ${deps.manager.toUpperCase()})</span>
            <span class="px-2.5 py-1 rounded-lg text-xs font-bold ${deps.pm2 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">${deps.pm2 ? 'Installed' : 'Missing'}</span>
        </div>
    `;

    if (!isAllInstalled) {
        actionArea.innerHTML = `<button onclick="installDeps()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-lg transition"><i class="fa fa-download mr-1"></i> Install Dependencies (${deps.manager.toUpperCase()})</button>`;
    } else {
        actionArea.innerHTML = `<button onclick="uninstallDeps()" class="px-4 py-2 bg-rose-600/20 hover:bg-rose-600 text-rose-400 hover:text-white text-xs font-bold rounded-xl border border-rose-500/30 transition"><i class="fa fa-trash mr-1"></i> Uninstall Node Environment</button>`;
    }
}

async function installDeps() {
    Swal.fire({
        title: 'Sedang Menginstal...',
        text: 'Mohon tunggu, sedang mendownload Node, NPM, dan PM2 sesuai OS kamu.',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });
    const fd = new FormData();
    const res = await fetch('/websites/node/api/install', { method: 'POST', body: fd });
    const data = await res.json();
    Swal.close();
    if (data.success) {
        Swal.fire('Berhasil!', 'Semua dependencies berhasil diinstal.', 'success');
        fetchStatus();
    } else {
        Swal.fire('Gagal!', data.error, 'error');
    }
}

async function uninstallDeps() {
    Swal.fire({
        title: 'Yakin ingin uninstall?',
        text: 'Node, NPM, dan PM2 akan dihapus dari sistem.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Ya, Hapus!'
    }).then(async (result) => {
        if (result.isConfirmed) {
            Swal.fire({ title: 'Menghapus...', didOpen: () => { Swal.showLoading(); } });
            const fd = new FormData();
            const res = await fetch('/websites/node/api/uninstall', { method: 'POST', body: fd });
            const data = await res.json();
            Swal.close();
            if (data.success) {
                Swal.fire('Berhasil!', 'Dependencies berhasil di-uninstall.', 'success');
                fetchStatus();
            } else {
                Swal.fire('Gagal!', data.error, 'error');
            }
        }
    });
}

function renderProjects(projects) {
    const tbody = document.getElementById('project-table-body');
    if (projects.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="p-6 text-center text-slate-500">Belum ada project Node.js yang ditambahkan.</td></tr>`;
        return;
    }
    tbody.innerHTML = projects.map(p => `
        <tr class="hover:bg-slate-800/30 transition">
            <td class="p-3 font-bold text-white">${p.name}</td>
            <td class="p-3 text-slate-400 font-mono">${p.path}</td>
            <td class="p-3 text-indigo-400 font-mono">${p.start_cmd}</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400">${p.status}</span></td>
            <td class="p-3 text-right space-x-2">
                <button onclick="viewLogs('${p.name}')" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"><i class="fa fa-terminal"></i> Logs</button>
                <button onclick="deleteProject('${p.name}')" class="px-2.5 py-1.5 bg-rose-500/10 hover:bg-rose-600 text-rose-400 hover:text-white rounded-lg"><i class="fa fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

function openAddModal() { document.getElementById('modal-add').classList.remove('hidden'); document.getElementById('modal-add').classList.add('flex'); }
function closeAddModal() { document.getElementById('modal-add').classList.remove('flex'); document.getElementById('modal-add').classList.add('hidden'); }

async function submitAddProject(e) {
    e.preventDefault();
    const form = document.getElementById('form-add-project');
    const fd = new FormData(form);

    Swal.fire({
        title: 'Deploying Project...',
        text: 'Mengkloning/Memuat project, menjalankan npm i, dan start PM2...',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });

    const res = await fetch('/websites/node/api/add', { method: 'POST', body: fd });
    const data = await res.json();
    Swal.close();

    if (data.success) {
        Swal.fire('Berhasil!', 'Project berhasil dideploy!', 'success');
        closeAddModal();
        form.reset();
        fetchStatus();
    } else {
        Swal.fire('Gagal!', data.error, 'error');
    }
}

async function viewLogs(name) {
    const res = await fetch(`/websites/node/api/logs/${name}`);
    const data = await res.json();
    document.getElementById('log-content').innerText = data.logs;
    document.getElementById('modal-logs').classList.remove('hidden');
    document.getElementById('modal-logs').classList.add('flex');
}
function closeLogsModal() { document.getElementById('modal-logs').classList.remove('flex'); document.getElementById('modal-logs').classList.add('hidden'); }

async function deleteProject(name) {
    Swal.fire({
        title: `Hapus project ${name}?`,
        text: 'Folder project dan proses PM2 akan dihapus permanen!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Ya, Hapus!'
    }).then(async (result) => {
        if (result.isConfirmed) {
            const fd = new FormData();
            fd.append('name', name);
            const res = await fetch('/websites/node/api/delete', { method: 'POST', body: fd });
            const data = await res.json();
            if (data.success) {
                Swal.fire('Terhapus!', 'Project berhasil dihapus.', 'success');
                fetchStatus();
            } else {
                Swal.fire('Gagal!', data.error, 'error');
            }
        }
    });
}