// node_manager.js
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
        console.error("Failed to load node status", e);
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
            <span>PM2</span>
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
        title: 'Installing...',
        text: 'Please wait, downloading Node, NPM, and PM2 according to your OS.',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });
    const fd = new FormData();
    const res = await fetch('/websites/node/api/install', { method: 'POST', body: fd });
    const data = await res.json();
    Swal.close();
    if (data.success) {
        Swal.fire('Success!', 'All dependencies installed successfully.', 'success');
        fetchStatus();
    } else {
        Swal.fire('Failed!', data.error, 'error');
    }
}

async function uninstallDeps() {
    Swal.fire({
        title: 'Are you sure you want to uninstall?',
        text: 'Node, NPM, and PM2 will be removed from the system.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Delete!'
    }).then(async (result) => {
        if (result.isConfirmed) {
            Swal.fire({ title: 'Uninstalling...', didOpen: () => { Swal.showLoading(); } });
            const fd = new FormData();
            const res = await fetch('/websites/node/api/uninstall', { method: 'POST', body: fd });
            const data = await res.json();
            Swal.close();
            if (data.success) {
                Swal.fire('Success!', 'Dependencies uninstalled successfully.', 'success');
                fetchStatus();
            } else {
                Swal.fire('Failed!', data.error, 'error');
            }
        }
    });
}

function toggleSourceInput() {
    const type = document.getElementById('source_type').value;
    const gitDiv = document.getElementById('input-git');
    const uploadDiv = document.getElementById('input-upload');
    const gitInput = document.getElementById('source_val');
    const uploadInput = document.getElementById('source_file');

    if (type === 'git') {
        gitDiv.classList.remove('hidden');
        uploadDiv.classList.add('hidden');
        gitInput.required = true;
        uploadInput.required = false;
    } else {
        gitDiv.classList.add('hidden');
        uploadDiv.classList.remove('hidden');
        gitInput.required = false;
        uploadInput.required = true;
    }
}

async function projectAction(name, actionType) {
    Swal.fire({
        title: `Executing ${actionType.toUpperCase()}...`,
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });

    const fd = new FormData();
    fd.append('name', name);
    fd.append('action_type', actionType);

    const res = await fetch('/websites/node/api/action', { method: 'POST', body: fd });
    const data = await res.json();
    
    Swal.close();
    if (data.success) {
        fetchStatus();
    } else {
        Swal.fire('Failed!', data.error, 'error');
    }
}

function renderProjects(projects) {
    const tbody = document.getElementById('project-table-body');
    if (projects.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="p-6 text-center text-slate-500">No Node.js projects added yet.</td></tr>`;
        return;
    }
    tbody.innerHTML = projects.map(p => {
        let statusStyle = '';
        if (p.status === 'online') {
            statusStyle = 'background-color: rgb(16 185 129 / 0.2) !important; color: rgb(52 211 153) !important;';
        } else if (p.status === 'errored') {
            statusStyle = 'background-color: rgb(239 68 68 / 0.2) !important; color: rgb(248 113 113) !important;';
        } else if (p.status === 'stopping') {
            statusStyle = 'background-color: rgb(234 179 8 / 0.2) !important; color: rgb(250 204 21) !important;';
        } else if (p.status === 'stopped') {
            statusStyle = 'background-color: rgb(107 114 128 / 0.2) !important; color: rgb(156 163 175) !important;';
        }
        return `
        <tr class="hover:bg-slate-800/30 transition">
            <td class="p-3 font-bold text-white">${p.name}</td>
            <td class="p-3 text-slate-400 font-mono">${p.path}</td>
            <td class="p-3 text-indigo-400 font-mono">${p.start_cmd}</td>
            <td class="p-3">
                <span
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold capitalize"
                    style="${statusStyle}"
                >${p.status}</span>
            </td>
            <td class="p-3 text-right space-x-1">
                <!-- Power Controls -->
                <button onclick="projectAction('${p.name}', 'start')" title="Start" class="px-2 py-1.5 bg-emerald-500/10 hover:bg-emerald-600 text-emerald-400 hover:text-white rounded-lg transition"><i class="fa fa-play"></i></button>
                <button onclick="projectAction('${p.name}', 'stop')" title="Stop" class="px-2 py-1.5 bg-rose-500/10 hover:bg-rose-600 text-rose-400 hover:text-white rounded-lg transition"><i class="fa fa-stop"></i></button>
                <button onclick="projectAction('${p.name}', 'restart')" title="Restart" class="px-2 py-1.5 bg-amber-500/10 hover:bg-amber-600 text-amber-400 hover:text-white rounded-lg transition"><i class="fa fa-repeat"></i></button>
                <button onclick="projectAction('${p.name}', 'reload')" title="0-Downtime Reload" class="px-2 py-1.5 bg-blue-500/10 hover:bg-blue-600 text-blue-400 hover:text-white rounded-lg transition"><i class="fa fa-refresh"></i></button>
                
                <!-- Management -->
                <button onclick="openEditModal('${p.name}', '${p.start_cmd}')" title="Edit" class="px-2 py-1.5 ml-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg shadow"><i class="fa fa-edit"></i></button>
                <button onclick="viewLogs('${p.name}')" title="Logs" class="px-2 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"><i class="fa fa-terminal"></i></button>
                <button onclick="projectAction('${p.name}', 'flush')" title="Clear Logs" class="px-2 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"><i class="fa fa-eraser"></i></button>
                <button onclick="deleteProject('${p.name}')" title="Delete" class="px-2 py-1.5 ml-2 bg-rose-500/10 hover:bg-rose-600 text-rose-400 hover:text-white rounded-lg"><i class="fa fa-trash"></i></button>
            </td>
        </tr>
    `}).join('');
}

function openAddModal() { document.getElementById('modal-add').classList.remove('hidden'); document.getElementById('modal-add').classList.add('flex'); }
function closeAddModal() { document.getElementById('modal-add').classList.remove('flex'); document.getElementById('modal-add').classList.add('hidden'); }

async function submitAddProject(e) {
    e.preventDefault();
    const form = document.getElementById('form-add-project');
    const fd = new FormData(form);

    Swal.fire({
        title: 'Deploying Project...',
        text: 'Cloning/Loading project, running npm i, and starting PM2...',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });

    const res = await fetch('/websites/node/api/add', { method: 'POST', body: fd });
    const data = await res.json();
    Swal.close();

    if (data.success) {
        Swal.fire('Success!', 'Project deployed successfully!', 'success');
        closeAddModal();
        form.reset();
        fetchStatus();
    } else {
        Swal.fire('Failed!', data.error, 'error');
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
        title: `Delete project ${name}?`,
        text: 'Project folder and PM2 process will be permanently deleted!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, Delete!'
    }).then(async (result) => {
        if (result.isConfirmed) {
            const fd = new FormData();
            fd.append('name', name);
            const res = await fetch('/websites/node/api/delete', { method: 'POST', body: fd });
            const data = await res.json();
            if (data.success) {
                Swal.fire('Deleted!', 'Project deleted successfully.', 'success');
                fetchStatus();
            } else {
                Swal.fire('Failed!', data.error, 'error');
            }
        }
    });
}

function openEditModal(name, startCmd) {
    document.getElementById('edit-name').value = name;
    document.getElementById('edit-start-cmd').value = startCmd;
    document.getElementById('modal-edit').classList.remove('hidden');
    document.getElementById('modal-edit').classList.add('flex');
}

function closeEditModal() {
    document.getElementById('modal-edit').classList.remove('flex');
    document.getElementById('modal-edit').classList.add('hidden');
    document.getElementById('form-edit-project').reset();
}

async function submitEditProject(e) {
    e.preventDefault();
    const form = document.getElementById('form-edit-project');
    const fd = new FormData(form);

    Swal.fire({
        title: 'Updating Project...',
        text: 'Applying changes and restarting PM2 process...',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });

    try {
        const res = await fetch('/websites/node/api/modify', { method: 'POST', body: fd });
        const data = await res.json();
        Swal.close();

        if (data.success) {
            Swal.fire('Success!', 'Project updated and restarted!', 'success');
            closeEditModal();
            fetchStatus();
        } else {
            Swal.fire('Failed!', data.error || 'An unknown error occurred.', 'error');
        }
    } catch (err) {
        Swal.close();
        Swal.fire('Error!', 'Failed to connect to the server.', 'error');
    }
}