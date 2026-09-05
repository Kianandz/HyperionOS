// Buka Modal & Load Log UFW
async function openLogsModal() {
    openModal('logsModal');
    await fetchUfwLogs();
}

// Ambil data log dari Server
async function fetchUfwLogs() {
    const container = document.getElementById('log-content-container');
    container.innerHTML = '<div class="text-center text-slate-500 py-8"><i class="fa fa-spinner fa-spin text-xl"></i> Loading logs...</div>';
    
    try {
        const res = await fetch('/firewall/logs');
        const json = await res.json();
        
        if (json.status === 'success') {
            container.textContent = json.logs;
            // Auto scroll ke paling bawah log
            container.scrollTop = container.scrollHeight;
        } else {
            container.innerHTML = `<span class="text-rose-400">Gagal mengambil log: ${json.message}</span>`;
        }
    } catch (err) {
        container.innerHTML = `<span class="text-rose-400">Error jaringan: ${err.message}</span>`;
    }
}