async function openContainerSettings(containerId) {
    document.getElementById('settings-modal').classList.remove('hidden');
    showSettingsTab('config');
    document.getElementById('settings-modal').dataset.containerId = containerId;
    document.getElementById('ports-list').innerHTML = '';
    document.getElementById('volumes-list').innerHTML = '';
    document.getElementById('envs-list').innerHTML = '';

    try {
        const res = await fetch(`/docker/api/container/${containerId}`);
        const data = await res.json();
        
        if(data.status !== "error") {
            document.getElementById('conf-image').value = data.image || '';
            document.getElementById('conf-tag').value = data.tag || 'latest';
            document.getElementById('conf-title').value = data.name || '';
            document.getElementById('conf-icon').value = data.icon || '';
            if(document.getElementById('conf-icon-preview')) document.getElementById('conf-icon-preview').src = data.icon || 'https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/docker.png';

            if (data.ports) data.ports.forEach(p => addDynamicRow('ports-list', 'port', p.host, p.container, p.protocol));
            if (data.volumes) data.volumes.forEach(v => addDynamicRow('volumes-list', 'volume', v.host, v.container));
            if (data.env) data.env.forEach(envStr => {
                const parts = envStr.split('=');
                addDynamicRow('envs-list', 'env', parts[0] || '', parts.slice(1).join('=') || '');
            });

            const termOutput = document.getElementById('term-output');
            const termInput = document.getElementById('term-input');
            if (data.status === 'running') {
                termOutput.innerHTML = `Connected to container terminal (${data.name}).<br>root@container:/# `;
                termInput.disabled = false;
                termInput.placeholder = "Enter command...";
            } else {
                termOutput.innerHTML = `Container is currently stopped (${data.status}). Terminal unavailable.`;
                termInput.disabled = true;
                termInput.placeholder = "Container is stopped...";
            }
        }
    } catch (e) { console.error("Gagal load config:", e); }

    try {
        const composeRes = await fetch(`/docker/api/export/${containerId}`);
        const composeData = await composeRes.json();
        if(composeData.status === "success") {
            document.getElementById('tab-export').innerHTML = `
                <div class="space-y-3">
                    <textarea class="w-full h-72 bg-slate-950 border border-white/10 rounded-lg p-4 font-mono text-xs text-slate-300" readonly>${composeData.compose}</textarea>
                    <div class="flex justify-end">
                        <button onclick="downloadCompose('${containerId}')" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition cursor-pointer flex items-center gap-2">
                            <i class="fa fa-solid fa-download"></i> Download docker-compose.yml
                        </button>
                    </div>
                </div>
            `;
        }
    } catch (e) { console.error("Gagal load export:", e); }

    try {
        const logsRes = await fetch(`/docker/api/logs/${containerId}`);
        const logsData = await logsRes.json();
        if (document.getElementById('logs-output')) document.getElementById('logs-output').textContent = logsData.logs || "No logs available or container stopped.";
    } catch (e) { console.error("Gagal load logs:", e); }
}

function closeSettingsModal() { document.getElementById('settings-modal').classList.add('hidden'); }

function showSettingsTab(tabName) {
    ['config', 'terminal', 'logs', 'export'].forEach(t => {
        const tabEl = document.getElementById(`tab-${t}`);
        if(tabEl) tabEl.classList.add('hidden');
        const btn = document.getElementById(`tab-btn-${t}`);
        if(btn) btn.className = "text-sm font-medium text-slate-400 hover:text-slate-200 pb-2 transition-all";
    });
    
    const activeTab = document.getElementById(`tab-${tabName}`);
    if(activeTab) activeTab.classList.remove('hidden');
    const activeBtn = document.getElementById(`tab-btn-${tabName}`);
    if(activeBtn) activeBtn.className = "text-sm font-medium text-blue-400 border-b-2 border-blue-400 pb-2 transition-all";
}

function addDynamicRow(containerId, type, val1 = '', val2 = '', val3 = 'tcp') {
    const container = document.getElementById(containerId);
    if (!container) return;
    const row = document.createElement('div');
    row.className = 'flex gap-2 items-center group';
    
    if (type === 'port') {
        row.innerHTML = `<input type="text" value="${val1}" class="flex-[5] bg-slate-950 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-400 outline-none">
            <input type="text" value="${val2}" class="flex-[5] bg-slate-950 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-400 outline-none">
            <select class="flex-[2] bg-slate-950 border border-white/10 rounded-lg px-2 py-1.5 text-sm text-white focus:border-blue-500 outline-none">
                <option value="tcp" ${val3 === 'tcp' ? 'selected' : ''}>TCP</option>
                <option value="udp" ${val3 === 'udp' ? 'selected' : ''}>UDP</option>
            </select>
            <button type="button" onclick="this.parentElement.remove()" class="w-8 h-8 text-slate-500 hover:text-rose-500 cursor-pointer"><i class="fa fa-solid fa-close"></i></button>`;
    } else if (type === 'volume') {
        row.innerHTML = `<input type="text" value="${val1}" class="flex-[6] bg-slate-950 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-400 outline-none">
            <input type="text" value="${val2}" class="flex-[6] bg-slate-950 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-400 outline-none">
            <button type="button" onclick="this.parentElement.remove()" class="w-8 h-8 text-slate-500 hover:text-rose-500 cursor-pointer"><i class="fa fa-solid fa-close"></i></button>`;
    } else if (type === 'env') {
        row.innerHTML = `<input type="text" value="${val1}" class="flex-[5] bg-slate-950 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-400 outline-none uppercase">
            <input type="text" value="${val2}" class="flex-[7] bg-slate-950 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white focus:border-emerald-400 outline-none">
            <button type="button" onclick="this.parentElement.remove()" class="w-8 h-8 text-slate-500 hover:text-rose-500 cursor-pointer"><i class="fa fa-solid fa-close"></i></button>`;
    }
    container.appendChild(row);
}

function downloadCompose(containerId) {
    const textarea = document.querySelector('#tab-export textarea');
    if (!textarea) return;
    const blob = new Blob([textarea.value], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `docker-compose-${containerId}.yml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', () => {
    const termInput = document.getElementById('term-input');
    if (termInput) {
        termInput.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter') {
                const command = termInput.value.trim();
                if (!command) return;
                const containerId = document.getElementById('settings-modal').dataset.containerId;
                const termOutput = document.getElementById('term-output');

                termOutput.innerHTML += `\n<span class="text-white">root@container:/# ${command}</span>\n`;
                termInput.value = '';
                termInput.disabled = true;

                try {
                    const formData = new FormData();
                    formData.append('container_id', containerId);
                    formData.append('command', command);

                    const response = await fetch('/docker/api/terminal', { method: 'POST', body: formData });
                    const result = await response.json();

                    if (result.status === 'success') {
                        termOutput.innerHTML += `<span class="text-slate-300">${result.output}</span>`;
                    } else {
                        termOutput.innerHTML += `<span class="text-rose-500">Error: ${result.message}</span>`;
                    }
                } catch (error) {
                    termOutput.innerHTML += `<span class="text-rose-500">Error: Gagal konek server. ${error.message}</span>`;
                }
                
                termOutput.innerHTML += '\nroot@container:/# ';
                termOutput.scrollTop = termOutput.scrollHeight; 
                termInput.disabled = false;
                termInput.focus();
            }
        });
    }
});

async function saveContainerConfig() {
    const containerId = document.getElementById('settings-modal').dataset.containerId;
    const ports = {};
    document.querySelectorAll('#ports-list > div').forEach(row => {
        const inputs = row.querySelectorAll('input, select');
        if(inputs[0].value && inputs[1].value) ports[`${inputs[1].value}/${inputs[2].value}`] = parseInt(inputs[0].value);
    });

    const volumes = [];
    document.querySelectorAll('#volumes-list > div').forEach(row => {
        const inputs = row.querySelectorAll('input');
        if(inputs[0].value && inputs[1].value) volumes.push(`${inputs[0].value}:${inputs[1].value}`);
    });

    const env = [];
    document.querySelectorAll('#envs-list > div').forEach(row => {
        const inputs = row.querySelectorAll('input');
        if(inputs[0].value) env.push(`${inputs[0].value}=${inputs[1].value}`);
    });

    const payload = {
        container_id: containerId,
        image: document.getElementById('conf-image').value,
        name: document.getElementById('conf-title').value,
        ports: ports, volumes: volumes, env: env,
        privileged: document.getElementById('conf-privileged').checked,
        mem_limit: document.getElementById('conf-mem').value + "m",
        cpu_shares: document.getElementById('conf-cpu').value === 'high' ? 2048 : (document.getElementById('conf-cpu').value === 'low' ? 512 : 1024),
        restart_policy: document.getElementById('conf-restart').value
    };

    Swal.fire({ title: 'Recreating...', background: '#0f172a', color: '#f8fafc', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

    try {
        const response = await fetch('/docker/api/container/update', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (result.status === 'success') {
            Swal.fire({ icon: 'success', title: 'Mantap!', background: '#0f172a', color: '#f8fafc', confirmButtonColor: '#10b981' }).then(() => window.location.reload());
        } else throw new Error(result.message);
    } catch (error) {
        Swal.fire({ icon: 'error', title: 'Gagal Update', text: error.message, background: '#0f172a', color: '#f8fafc', confirmButtonColor: '#ef4444' });
    }
}