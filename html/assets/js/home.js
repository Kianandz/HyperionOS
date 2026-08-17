async function fetchMetrics() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/metrics`);
        const data = await res.json();

        // System Info
        if (data.system) {
            document.getElementById('val-hostname').innerText = `Host: ${data.system.hostname}`;
            document.getElementById('val-uptime').innerText = data.system.uptime;
            document.getElementById('val-os').innerText = data.system.os;
            document.getElementById('val-cores').innerText = `${data.system.cpu_cores} Cores`;
            document.getElementById('val-processes').innerText = `${data.system.process_count} Tasks`;
        }

        // CPU Usage & Progress Bar
        document.getElementById('val-cpu').innerText = `${data.cpu_percent}%`;
        document.getElementById('bar-cpu').style.width = `${data.cpu_percent}%`;

        // RAM Usage & Progress Bar
        document.getElementById('val-ram').innerText = `${data.ram.used_gb} / ${data.ram.total_gb} GB`;
        document.getElementById('val-ram-percent').innerText = `${data.ram.percent}% used`;
        document.getElementById('bar-ram').style.width = `${data.ram.percent}%`;

        // Network
        document.getElementById('val-net-down').innerText = `${data.network.download_kbps} KB/s`;
        document.getElementById('val-net-up').innerText = `${data.network.upload_kbps} KB/s`;

        // Disk Storage
        const diskContainer = document.getElementById('disk-list');
        diskContainer.innerHTML = '';
        data.disks.forEach(disk => {
            diskContainer.innerHTML += `
                <div class="space-y-1">
                    <div class="flex justify-between text-sm">
                        <span class="font-mono text-indigo-300">${disk.mountpoint} (${disk.device})</span>
                        <span class="text-slate-400">${disk.used_gb} GB / ${disk.total_gb} GB (${disk.percent}%)</span>
                    </div>
                    <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div class="bg-indigo-500 h-full rounded-full transition-all duration-500" style="width: ${disk.percent}%"></div>
                    </div>
                </div>
            `;
        });
    } catch (err) {
        console.error("Gagal konek ke FastAPI:", err);
    }
}

setInterval(fetchMetrics, 2000);
fetchMetrics();