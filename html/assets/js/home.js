const DOM = {
    hostname: document.getElementById('val-hostname'),
    uptime: document.getElementById('val-uptime'),
    os: document.getElementById('val-os'),
    cores: document.getElementById('val-cores'),
    processes: document.getElementById('val-processes'),
    cpuVal: document.getElementById('val-cpu'),
    cpuBar: document.getElementById('bar-cpu'),
    ramVal: document.getElementById('val-ram'),
    ramPercent: document.getElementById('val-ram-percent'),
    ramBar: document.getElementById('bar-ram'),
    netDown: document.getElementById('val-net-down'),
    netUp: document.getElementById('val-net-up'),
    diskList: document.getElementById('disk-list')
};

async function fetchMetrics() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/metrics`);
        if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
        
        const data = await res.json();

        // Update Text (TIDAK ADA LAGI INJECT SVG DISINI)
        if (data.system) {
            // Karena SVG udah ditaro di HTML, kita cuma ubah text node terakhirnya
            DOM.hostname.lastChild.nodeValue = ` Host: ${data.system.hostname}`;
            DOM.uptime.innerText = data.system.uptime;
            DOM.os.innerText = data.system.os;
            DOM.cores.innerText = data.system.cpu_cores;
            DOM.processes.innerText = data.system.process_count;
        }

        // CPU & RAM
        DOM.cpuVal.innerText = `${data.cpu_percent}%`;
        DOM.cpuBar.style.width = `${data.cpu_percent}%`;

        DOM.ramVal.innerText = `${data.ram.used_gb} / ${data.ram.total_gb} GB`;
        DOM.ramPercent.innerText = `${data.ram.percent}% used`;
        DOM.ramBar.style.width = `${data.ram.percent}%`;

        // Network
        DOM.netDown.innerHTML = `${data.network.download_kbps} <span class="text-sm text-emerald-500/50 font-normal">KB/s</span>`;
        DOM.netUp.innerHTML = `${data.network.upload_kbps} <span class="text-sm text-pink-500/50 font-normal">KB/s</span>`;

        // Disk (Flat Solid Design)
        const fragment = document.createDocumentFragment();
        data.disks.forEach(disk => {
            const diskEl = document.createElement('div');
            diskEl.className = 'space-y-2';
            diskEl.innerHTML = `
                <div class="flex justify-between items-center text-sm">
                    <span class="font-mono text-slate-300 bg-slate-800 px-2.5 py-1 rounded-md text-[11px] font-semibold tracking-wide">${disk.mountpoint}</span>
                    <span class="text-slate-400 text-xs font-mono">${disk.used_gb} / ${disk.total_gb} GB <span class="text-indigo-400 ml-1 font-bold">(${disk.percent}%)</span></span>
                </div>
                <div class="w-full bg-slate-950/80 rounded-full h-2 overflow-hidden">
                    <div class="bg-indigo-500 h-full rounded-full transition-all duration-700 ease-out" style="width: ${disk.percent}%"></div>
                </div>
            `;
            fragment.appendChild(diskEl);
        });
        
        DOM.diskList.innerHTML = '';
        DOM.diskList.appendChild(fragment);

    } catch (err) {
        console.error('[Dashboard] Error:', err.message);
    }
}

fetchMetrics();
setInterval(fetchMetrics, 2000);