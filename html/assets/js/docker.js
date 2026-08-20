async function fetchDockerData() {
    try {
        const resOverview = await fetch(`${API_BASE}/docker/overview`);
        const overview = await resOverview.json();

        if (overview.status === 'online') {
            document.getElementById('dk-running').innerText = overview.containers_running;
            document.getElementById('dk-stopped').innerText = overview.containers_stopped;
            document.getElementById('dk-images').innerText = overview.images_count;
            document.getElementById('docker-version').innerText = `Version: ${overview.docker_version}`;
        } else {
            document.getElementById('docker-version').innerText = "Status: Offline";
            console.error("Docker error:", overview.error);
        }

        const resContainers = await fetch(`${API_BASE}/docker/containers`);
        const containers = await resContainers.json();
        const containerList = document.getElementById('docker-container-list');
        containerList.innerHTML = '';

        if (containers.length === 0) {
            containerList.innerHTML = `<p class="col-span-full text-center text-slate-500 py-10">Container not found</p>`;
            return;
        }

        containers.forEach(c => {
            const isRunning = c.status === 'running';
            // Bikin efek nyala buat indikator status
            const statusColor = isRunning 
                ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]' 
                : 'bg-rose-400 shadow-[0_0_8px_rgba(251,113,133,0.8)]';

            containerList.innerHTML += `
    <div onclick="openDockerModal('${c.id}')" class="bg-white/5 hover:bg-white/10 border border-white/5 backdrop-blur-sm rounded-2xl p-4 flex flex-col items-center justify-center relative group transition-all duration-300 h-36 cursor-pointer">
        
        <!-- Titik Status di pojok -->
        <div class="absolute top-3 right-3 w-2.5 h-2.5 rounded-full ${statusColor}" title="${c.status}"></div>
        
        <div class="w-14 h-14 rounded-2xl bg-slate-800/80 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform shadow-inner border border-white/5">
            <i class="fa-brands fa-docker text-3xl text-blue-400/80"></i>
        </div>
        
        <span class="text-sm font-medium text-slate-200 truncate w-full text-center" title="${c.name}">
            ${c.name}
        </span>
        
        <!-- Overlay Action -->
        <div class="absolute inset-0 bg-slate-900/90 backdrop-blur-md rounded-2xl flex items-center justify-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            ${isRunning 
                ? `<button onclick="event.stopPropagation(); handleDockerAction('${c.id}', 'stop')" class="text-yellow-400 hover:text-yellow-300 hover:scale-110 transition-transform"><i class="fa fa-solid fa-pause text-2xl"></i></button>`
                : `<button onclick="event.stopPropagation(); handleDockerAction('${c.id}', 'start')" class="text-emerald-400 hover:text-emerald-300 hover:scale-110 transition-transform"><i class="fa fa-solid fa-play text-2xl"></i></button>`
            }
            <button onclick="event.stopPropagation(); handleDockerAction('${c.id}', 'restart')" class="text-blue-400 hover:text-blue-300 hover:scale-110 transition-transform"><i class="fa fa-solid fa-rotate-right text-2xl"></i></button>
            <button onclick="event.stopPropagation(); handleDockerAction('${c.id}', 'delete')" class="text-rose-400 hover:text-rose-300 hover:scale-110 transition-transform"><i class="fa fa-solid fa-trash text-2xl"></i></button>
        </div>
    </div>
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

// Bikin variabel global buat nyimpen data container sementara
let currentDockerData = null; 

async function openDockerModal(containerId) {
    const modal = document.getElementById('docker-modal');
    modal.classList.remove('hidden');
    
    // State Loading
    document.getElementById('modal-c-name').innerText = "Loading details...";
    document.getElementById('modal-tab-content').innerHTML = `<p class="text-center text-slate-500 py-10">Fetching data...</p>`;

    try {
        const res = await fetch(`${API_BASE}/docker/container/${containerId}`);
        const data = await res.json();

        if(data.status === 'error') throw new Error(data.message);

        // Simpen ke variabel global biar fungsi showTab() bisa baca datanya
        currentDockerData = data; 
        document.getElementById('modal-c-name').innerText = data.name;
        
        // Panggil tab 'info' buat nampilin data default pas modal baru kebuka
        showTab('info');

        // Render tombol aksi di bawah
        document.getElementById('modal-actions-container').innerHTML = `
            <button onclick="handleDockerAction('${data.id}', 'restart'); closeDockerModal()" class="flex-1 bg-blue-500/10 border border-blue-500/30 text-blue-400 py-2 rounded-xl hover:bg-blue-500/20 transition">Restart</button>
            <button onclick="handleDockerAction('${data.id}', 'delete'); closeDockerModal()" class="flex-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 py-2 rounded-xl hover:bg-rose-500/20 transition">Delete</button>
        `;

    } catch (err) {
        document.getElementById('modal-c-name').innerText = "Error loading data";
        document.getElementById('modal-tab-content').innerHTML = `<p class="text-rose-400">Failed to fetch API.</p>`;
        console.error(err);
    }
}

// Fungsi baru buat ngurus gonta-ganti tab
function showTab(tabName) {
    if (!currentDockerData) return;
    const data = currentDockerData;
    const content = document.getElementById('modal-tab-content');
    
    // Ngatur efek visual garis bawah/warna di menu tab yang lagi aktif
    ['info', 'env', 'volumes'].forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        if(btn) {
            btn.className = (t === tabName) 
                ? "text-sm font-medium text-blue-400 border-b border-blue-400 pb-1 transition-all" 
                : "text-sm font-medium text-slate-400 hover:text-slate-200 pb-1 transition-all";
        }
    });

    // Injeksi data HTML tergantung lu ngeklik tab yang mana
    if(tabName === 'info') {
        content.innerHTML = `
            <div class="space-y-3">
                <p class="border-b border-white/5 pb-2"><span class="text-slate-400 block mb-1">Container ID</span> <span class="font-mono text-slate-200">${data.id}</span></p>
                <p class="border-b border-white/5 pb-2"><span class="text-slate-400 block mb-1">Image</span> <span class="text-slate-200">${data.image || 'N/A'}</span></p>
                <p><span class="text-slate-400 block mb-1">Command</span> <span class="font-mono text-emerald-400 bg-slate-900 px-2 py-1 rounded inline-block">${(data.cmd || []).join(' ')}</span></p>
            </div>
        `;
    } else if(tabName === 'env') {
        const envList = (data.env || []).join('\n') || 'No Environment Variables';
        content.innerHTML = `<pre class="text-xs bg-slate-900 p-3 rounded-lg overflow-x-auto text-blue-300 font-mono border border-white/5">${envList}</pre>`;
    } else if(tabName === 'volumes') {
        const volList = (data.volumes || []).map(v => `<li class="mb-2 bg-slate-900/50 p-2 rounded">${v}</li>`).join('') || 'No Volumes Mapped';
        content.innerHTML = `<ul class="text-xs list-none font-mono">${volList}</ul>`;
    }
}

function closeDockerModal() {
    document.getElementById('docker-modal').classList.add('hidden');
    currentDockerData = null; // Clear memory
}

const mockApps = [
    { name: 'Nginx', image: 'nginx:latest', desc: 'High performance web server.', icon: 'fa fa-server', color: 'text-emerald-400' },
    { name: 'Redis', image: 'redis:alpine', desc: 'In-memory data structure store.', icon: 'fa fa-database', color: 'text-red-400' },
    { name: 'MySQL', image: 'mysql:8', desc: 'Popular relational database.', icon: 'fa fa-database', color: 'text-blue-400' },
    { name: 'Portainer', image: 'portainer/portainer-ce', desc: 'Container Management UI.', icon: 'fa fa-docker', color: 'text-cyan-400' },
    { name: 'Ubuntu', image: 'ubuntu:latest', desc: 'Base Ubuntu image.', icon: 'fa fa-linux', color: 'text-orange-400' }
];

function openAppStore() {
    const modal = document.getElementById('appstore-modal');
    modal.classList.remove('hidden');
    
    const list = document.getElementById('appstore-list');
    list.innerHTML = mockApps.map(app => `
        <div class="bg-slate-900/50 border border-white/5 rounded-2xl p-5 flex flex-col items-center text-center hover:bg-slate-900 hover:border-white/10 transition-all group">
            <div class="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center mb-4 text-3xl ${app.color} group-hover:scale-110 transition-transform border border-white/5 shadow-inner">
                <i class="fa-brands ${app.icon}"></i>
            </div>
            <h4 class="text-white font-bold mb-1">${app.name}</h4>
            <p class="text-xs text-slate-400 mb-5 flex-1">${app.desc}</p>
            <button onclick="installApp('${app.image}', this)" class="w-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 py-2 rounded-xl text-sm hover:bg-emerald-500/20 transition font-medium">
                Install
            </button>
        </div>
    `).join('');
}

function closeAppStore() {
    document.getElementById('appstore-modal').classList.add('hidden');
}

async function installApp(imageName, btnElement) {
    // Ubah UI tombol biar keliatan lagi loading
    const originalText = btnElement.innerHTML;
    btnElement.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Installing...`;
    btnElement.disabled = true;
    btnElement.classList.add('opacity-75', 'cursor-not-allowed');

    try {
        const res = await fetch(`${API_BASE}/docker/install`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_name: imageName })
        });
        
        const result = await res.json();

        if (res.ok) {
            // Kalo sukses, tutup modal App Store trus refresh list container di background
            closeAppStore();
            fetchDockerData(); 
            // Lu bisa tambahin notifikasi Toast di sini kalo ada
            console.log(result.message);
        } else {
            alert(`Gagal Install: ${result.detail}`);
        }
    } catch (err) {
        console.error("Install Error:", err);
        alert("Gagal konek ke API gan.");
    } finally {
        // Balikin tombol kaya semula kalo error (kalo sukses modalnya keburu nutup)
        btnElement.innerHTML = originalText;
        btnElement.disabled = false;
        btnElement.classList.remove('opacity-75', 'cursor-not-allowed');
    }
}