document.addEventListener('DOMContentLoaded', () => {
    // Muat token CF dari localStorage kalau udah pernah nyimpen
    const savedToken = localStorage.getItem('cf_api_token');
    if (savedToken) {
        document.getElementById('cfApiToken').value = savedToken;
        loadTunnels();
    }
    
    // Auto refresh log terminal tiap 3 detik
    fetchLogs();
    setInterval(fetchLogs, 3000);
});

function saveCFToken() {
    const token = document.getElementById('cfApiToken').value.trim();
    if (token) {
        localStorage.setItem('cf_api_token', token);
        Swal.fire({
            toast: true, position: 'top-end', showConfirmButton: false, timer: 3000,
            icon: 'success', title: 'API Token Disimpan', background: '#1e293b', color: '#fff'
        });
        loadTunnels();
    }
}

async function loadTunnels() {
    const token = localStorage.getItem('cf_api_token');
    const tunnelList = document.getElementById('tunnelList');
    
    if (!token) return;
    tunnelList.innerHTML = `<div class="text-center py-5 text-indigo-400"><i class="fa-solid fa-spinner fa-spin text-2xl"></i><p class="mt-2">Memuat Tunnels...</p></div>`;

    try {
        const response = await fetch('/cloudflared/api/tunnels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_token: token })
        });
        
        const data = await response.json();
        
        if (data.status === 'success' && data.tunnels) {
            tunnelList.innerHTML = '';
            if(data.tunnels.length === 0) {
                 tunnelList.innerHTML = '<div class="text-center py-5 opacity-50">Tidak ada tunnel di akun ini.</div>';
                 return;
            }

            data.tunnels.forEach(t => {
                const isOnline = t.status === 'active' || t.status === 'healthy';
                const statusColor = isOnline ? 'text-emerald-400' : 'text-rose-400';
                
                tunnelList.innerHTML += `
                    <div class="flex justify-between items-center p-4 bg-slate-950/50 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-colors">
                        <div>
                            <div class="font-semibold text-slate-200 flex items-center gap-2">
                                ${t.name} <span class="${statusColor} text-[10px] uppercase font-bold"><i class="fa-solid fa-circle text-[8px]"></i> ${t.status}</span>
                            </div>
                            <div class="text-xs font-mono text-slate-500 mt-1">${t.id}</div>
                        </div>
                        <button class="bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border border-slate-700">
                            Routes <i class="fa-solid fa-arrow-right ml-1"></i>
                        </button>
                    </div>
                `;
            });
        } else {
            tunnelList.innerHTML = `<div class="text-center py-5 text-rose-400">Gagal: ${data.message}</div>`;
        }
    } catch (err) {
        tunnelList.innerHTML = `<div class="text-center py-5 text-rose-400">Error memuat data.</div>`;
    }
}

async function fetchLogs() {
    const terminal = document.getElementById('logTerminal');
    if(!terminal) return;

    try {
        const response = await fetch('/cloudflared/api/logs');
        const data = await response.json();
        
        if (data.status === 'success') {
            // Cuma update scroll kalau ada perubahan log biar ngga lompat-lompat
            const isScrolledToBottom = terminal.scrollHeight - terminal.clientHeight <= terminal.scrollTop + 10;
            terminal.textContent = data.logs || 'Tidak ada log terbaru.';
            
            if (isScrolledToBottom) {
                terminal.scrollTop = terminal.scrollHeight;
            }
        }
    } catch (err) {
        console.error("Gagal load logs:", err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const savedToken = localStorage.getItem('cf_api_token');
    if (savedToken) {
        document.getElementById('cfApiToken').value = savedToken;
        loadTunnels();
    }
    
    fetchLogs();
    setInterval(fetchLogs, 3000);
});

function saveCFToken() {
    const token = document.getElementById('cfApiToken').value.trim();
    if (token) {
        localStorage.setItem('cf_api_token', token);
    }
}

async function loadTunnels() {
    const token = localStorage.getItem('cf_api_token');
    const tunnelList = document.getElementById('tunnelList');
    
    if (!token) return;
    tunnelList.innerHTML = `<div class="text-center py-5 text-indigo-400"><i class="fa-solid fa-spinner fa-spin text-2xl"></i><p class="mt-2">Memuat Tunnels...</p></div>`;

    try {
        const response = await fetch('/cloudflared/api/tunnels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_token: token })
        });
        
        const data = await response.json();
        
        if (data.status === 'success' && data.tunnels) {
            tunnelList.innerHTML = '';
            if(data.tunnels.length === 0) {
                 tunnelList.innerHTML = '<div class="text-center py-5 opacity-50">Tidak ada tunnel di akun ini.</div>';
                 return;
            }

            data.tunnels.forEach(t => {
                const isOnline = t.status === 'active' || t.status === 'healthy';
                const statusColor = isOnline ? 'text-emerald-400' : 'text-rose-400';
                
                tunnelList.innerHTML += `
                    <div class="flex justify-between items-center p-4 bg-slate-950/50 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-colors">
                        <div>
                            <div class="font-semibold text-slate-200 flex items-center gap-2">
                                ${t.name} <span class="${statusColor} text-[10px] uppercase font-bold"><i class="fa-solid fa-circle text-[8px]"></i> ${t.status}</span>
                            </div>
                            <div class="text-xs font-mono text-slate-500 mt-1">${t.id}</div>
                        </div>
                        <button class="bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border border-slate-700">
                            Routes <i class="fa-solid fa-arrow-right ml-1"></i>
                        </button>
                    </div>
                `;
            });
        } else {
            tunnelList.innerHTML = `<div class="text-center py-5 text-rose-400">Gagal: ${data.message}</div>`;
        }
    } catch (err) {
        tunnelList.innerHTML = `<div class="text-center py-5 text-rose-400">Error memuat data.</div>`;
    }
}

async function fetchLogs() {
    const terminal = document.getElementById('logTerminal');
    if(!terminal) return;

    try {
        const response = await fetch('/cloudflared/api/logs');
        const data = await response.json();
        
        if (data.status === 'success') {
            const isScrolledToBottom = terminal.scrollHeight - terminal.clientHeight <= terminal.scrollTop + 10;
            terminal.textContent = data.logs || 'Tidak ada log terbaru.';
            
            if (isScrolledToBottom) {
                terminal.scrollTop = terminal.scrollHeight;
            }
        }
    } catch (err) {
        console.error("Gagal load logs:", err);
    }
}

// Tambahan fungsi untuk tombol Start / Stop
// Timpa fungsi toggleService di cloudflared.js dengan ini:
async function toggleService(action) {
    try {
        const response = await fetch('/cloudflared/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action }) // Kirim payload sesuai request backend
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            Swal.fire({
                toast: true, position: 'top-end', showConfirmButton: false, timer: 3000,
                icon: 'success', title: `Daemon ${action} sukses`, background: '#1e293b', color: '#fff'
            });
            setTimeout(() => window.location.reload(), 1500);
        } else {
            Swal.fire({
                toast: true, position: 'top-end', showConfirmButton: false, timer: 3000,
                icon: 'error', title: data.message || `Gagal ${action} daemon`, background: '#1e293b', color: '#fff'
            });
        }
    } catch (err) {
        console.error(`Gagal ${action} service:`, err);
    }
}