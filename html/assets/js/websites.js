let currentMode = 'simple';

function openModalWebsite() {
    document.getElementById('web-domain').value = '';
    document.getElementById('web-domain').readOnly = false;
    document.getElementById('web-raw-config').value = '';
    switchWebTab('simple');
    document.getElementById('modal-website').classList.remove('hidden');
}

function closeModalWebsite() {
    document.getElementById('modal-website').classList.add('hidden');
}

function switchWebTab(mode) {
    currentMode = mode;
    document.getElementById('web-mode').value = mode;
    
    const btnSimple = document.getElementById('tab-btn-simple');
    const btnAdv = document.getElementById('tab-btn-advanced');
    const wrapSimple = document.getElementById('wrapper-simple-mode');
    const wrapAdv = document.getElementById('wrapper-advanced-mode');

    if (mode === 'simple') {
        btnSimple.className = "px-3 py-1.5 rounded-md font-medium text-white bg-indigo-600 transition";
        btnAdv.className = "px-3 py-1.5 rounded-md font-medium text-slate-400 hover:text-white transition";
        wrapSimple.classList.remove('hidden');
        wrapAdv.classList.add('hidden');
    } else {
        btnAdv.className = "px-3 py-1.5 rounded-md font-medium text-white bg-indigo-600 transition";
        btnSimple.className = "px-3 py-1.5 rounded-md font-medium text-slate-400 hover:text-white transition";
        wrapAdv.classList.remove('hidden');
        wrapSimple.classList.add('hidden');
    }
}

function toggleWebFields() {
    const type = document.getElementById('web-type').value;
    const fieldPort = document.getElementById('field-port');
    const fieldRoot = document.getElementById('field-root');
    const fieldPhp = document.getElementById('field-php-sock');

    fieldPort.classList.add('hidden');
    fieldRoot.classList.add('hidden');
    fieldPhp.classList.add('hidden');

    if (type === 'proxy') {
        fieldPort.classList.remove('hidden');
    } else if (type === 'static') {
        fieldRoot.classList.remove('hidden');
    } else if (type === 'php') {
        fieldRoot.classList.remove('hidden');
        fieldPhp.classList.remove('hidden');
    }
}

async function fetchServiceStatuses() {
    try {
        const res = await fetch(`${API_BASE}/websites/status`);
        const data = await res.json();
        
        const phpBadge = document.getElementById('badge-php-fpm');
        const phpStatus = data.php_fpm.status;

        if (phpStatus === 'active') {
            phpBadge.className = "px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400";
            phpBadge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> PHP-FPM Active`;
        } else if (phpStatus === 'inactive') {
            phpBadge.className = "px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 text-amber-400";
            phpBadge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400"></span> PHP-FPM Stopped`;
        } else {
            phpBadge.className = "px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 bg-slate-800 border border-slate-700 text-slate-400";
            phpBadge.innerHTML = `<span class="w-2 h-2 rounded-full bg-slate-500"></span> PHP-FPM Not Installed`;
        }
    } catch (err) {
        console.error("Gagal load status service:", err);
    }
}

async function handleNginxAction(action) {
    try {
        const res = await fetch(`${API_BASE}/websites/nginx/${action}`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            fetchServiceStatuses();
        } else {
            alert("Gagal: " + (data.detail || "Error menjalankan aksi Nginx"));
        }
    } catch (err) {
        alert("Gagal koneksi server!");
    }
}

async function fetchWebsites() {
    try {
        const res = await fetch(`${API_BASE}/websites/`);
        const data = await res.json();
        const tbody = document.getElementById('website-list-table');
        tbody.innerHTML = '';

        data.sites.forEach(site => {
            tbody.innerHTML += `
                <tr class="border-b border-slate-800/50 hover:bg-slate-800/20 transition">
                    <td class="p-4 font-mono text-indigo-400 font-medium">${site.domain}</td>
                    <td class="p-4 text-center">
                        <span class="px-4 py-2 rounded-full text-xs font-semibold ${site.is_active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400 border border-slate-700'}">
                            ${site.is_active ? 'Active' : 'Disabled'}
                        </span>
                    </td>
                    <td class="p-4 text-right space-x-2">
                        <button onclick="toggleStatus('${site.domain}')" class="px-4 py-2 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition" title="Toggle Active/Disable">
                            <i class="fa fa-solid ${site.is_active ? 'fa-pause text-amber-400' : 'fa-play text-emerald-400'} mr-1"></i> ${site.is_active ? 'Disable' : 'Enable'}
                        </button>
                        <button onclick="editConfig('${site.domain}')" class="px-4 py-2 text-xs bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 rounded transition border border-indigo-500/30">
                            <i class="fa fa-solid fa-code mr-1"></i> Config
                        </button>
                        <button onclick="deleteDomain('${site.domain}')" class="px-4 py-2 text-xs bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded transition border border-rose-500/20">
                            <i class="fa fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        console.error("Gagal load websites:", err);
    }
}

async function editConfig(domain) {
    try {
        const res = await fetch(`${API_BASE}/websites/config/${domain}`);
        const data = await res.json();
        
        document.getElementById('web-domain').value = domain;
        document.getElementById('web-domain').readOnly = true;
        document.getElementById('web-raw-config').value = data.config;
        
        switchWebTab('advanced');
        document.getElementById('modal-website').classList.remove('hidden');
    } catch (err) {
        alert("Gagal load file konfigurasi!");
    }
}

async function submitWebsite() {
    const payload = {
        domain: document.getElementById('web-domain').value.trim(),
        mode: currentMode,
        site_type: document.getElementById('web-type').value,
        port: parseInt(document.getElementById('web-port').value) || 8000,
        root_dir: document.getElementById('web-root').value,
        php_sock: document.getElementById('web-php-sock').value,
        max_body_size: document.getElementById('web-max-body').value,
        raw_config: document.getElementById('web-raw-config').value
    };

    if (!payload.domain) return alert("Domain wajib diisi!");

    const res = await fetch(`${API_BASE}/websites/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
        closeModalWebsite();
        loadWebsitesTab();
    } else {
        alert("Gagal menyimpan config:\n" + (data.detail || "Error Nginx syntax"));
    }
}

async function toggleStatus(domain) {
    await fetch(`${API_BASE}/websites/toggle/${domain}`, { method: 'POST' });
    loadWebsitesTab();
}

async function deleteDomain(domain) {
    if (confirm(`Yakin mau hapus config website ${domain}?`)) {
        await fetch(`${API_BASE}/websites/${domain}`, { method: 'DELETE' });
        loadWebsitesTab();
    }
}

function loadWebsitesTab() {
    fetchWebsites();
    fetchServiceStatuses();
}

onTabChange('websites', loadWebsitesTab);

let currentLogTarget = 'nginx';

// PHP-FPM Controls
async function handlePhpFpmAction(action) {
    try {
        const res = await fetch(`${API_BASE}/websites/php-fpm/${action}`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            fetchServiceStatuses();
        } else {
            alert("Gagal: " + (data.detail || "Error PHP-FPM"));
        }
    } catch (err) {
        alert("Gagal koneksi ke server!");
    }
}

// Log Viewer
async function openLogModal(target) {
    currentLogTarget = target;
    document.getElementById('log-modal-title').innerText = `System Logs: ${target.toUpperCase()}`;
    
    // Ganti ini biar flex-nya di-toggle pas buka
    const modal = document.getElementById('modal-logs');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    await refreshCurrentLog();
}

function closeLogModal() {
    const modal = document.getElementById('modal-logs');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

async function refreshCurrentLog() {
    const logBox = document.getElementById('log-content');
    logBox.innerText = 'Loading log stream...';
    try {
        const res = await fetch(`${API_BASE}/websites/logs/${currentLogTarget}`);
        const data = await res.json();
        if (res.ok) {
            logBox.innerText = data.logs || '--- Log Kosong / Tidak Ada Data ---';
            logBox.scrollTop = logBox.scrollHeight;
        } else {
            logBox.innerText = 'Gagal membaca log: ' + data.detail;
        }
    } catch (err) {
        logBox.innerText = 'Error koneksi server saat membaca log.';
    }
}

// PHP Config Manager (php.ini)
async function openPhpConfigModal() {
    try {
        const res = await fetch(`${API_BASE}/websites/php-config`);
        const data = await res.json();
        if (res.ok) {
            document.getElementById('php-ini-content').value = data.config;
            document.getElementById('php-ini-path-label').innerText = data.path;
            document.getElementById('modal-php-config').classList.remove('hidden');
        } else {
            alert("Gagal baca php.ini: " + data.detail);
        }
    } catch (err) {
        alert("Gagal koneksi ke server!");
    }
}

function closePhpConfigModal() {
    document.getElementById('modal-php-config').classList.add('hidden');
}

async function savePhpConfig() {
    const content = document.getElementById('php-ini-content').value;
    try {
        const res = await fetch(`${API_BASE}/websites/php-config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config: content })
        });
        const data = await res.json();
        if (res.ok) {
            alert("File php.ini berhasil di-update!");
            closePhpConfigModal();
            fetchServiceStatuses();
        } else {
            alert("Gagal menyimpan php.ini:\n" + data.detail);
        }
    } catch (err) {
        alert("Gagal koneksi ke server!");
    }
}