async function fetchDockerData() {
    try {
        const resOverview = await fetch(`${API_BASE}/docker/overview`);
        const dataOverview = await resOverview.json();

        if (dataOverview.status === "online") {
            document.getElementById('docker-version').innerText = `Docker v${dataOverview.docker_version}`;
            document.getElementById('dk-running').innerText = dataOverview.containers_running;
            document.getElementById('dk-stopped').innerText = dataOverview.containers_stopped;
            document.getElementById('dk-images').innerText = dataOverview.images_count;
        }

        const resContainers = await fetch(`${API_BASE}/docker/containers`);
        const containers = await resContainers.json();
        const tbody = document.getElementById('docker-container-list');
        tbody.innerHTML = '';

        if (containers.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-500">Container not found</td></tr>`;
            return;
        }

        containers.forEach(c => {
            const isRunning = c.status === 'running';
            tbody.innerHTML += `
                <tr class="border-b border-slate-800/50 hover:bg-slate-800/20">
                    <td class="p-4 font-mono text-xs text-indigo-400">${c.id}</td>
                    <td class="p-4 font-semibold text-white">${c.name}</td>
                    <td class="p-4 text-xs font-mono text-slate-400">${c.image}</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded text-xs ${isRunning ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}">
                            ${c.status}
                        </span>
                    </td>
                    <td class="p-4 text-right space-x-2">
                        ${isRunning 
                            ? `<button onclick="handleDockerAction('${c.id}', 'stop')" class="text-yellow-400 hover:text-yellow-300" title="Stop"><i class="fa-solid fa-pause"></i></button>`
                            : `<button onclick="handleDockerAction('${c.id}', 'start')" class="text-emerald-400 hover:text-emerald-300" title="Start"><i class="fa-solid fa-play"></i></button>`
                        }
                        <button onclick="handleDockerAction('${c.id}', 'restart')" class="text-blue-400 hover:text-blue-300" title="Restart"><i class="fa-solid fa-rotate-right"></i></button>
                        <button onclick="handleDockerAction('${c.id}', 'delete')" class="text-rose-400 hover:text-rose-300" title="Delete"><i class="fa-solid fa-trash"></i></button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        console.error("Failed load Docker data:", err);
    }
}

async function handleDockerAction(containerId, action) {
    if (action === 'delete' && !confirm(`Are you sure to delete container ${containerId}?`)) return;

    const res = await fetch(`${API_BASE}/docker/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ container_id: containerId, action: action })
    });

    if (res.ok) {
        fetchDockerData();
    } else {
        alert("Failed to exec container!");
    }
}

onTabChange('docker', fetchDockerData);