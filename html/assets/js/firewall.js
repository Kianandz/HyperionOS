let currentUfwStatus = 'inactive';

async function fetchUfwData() {
    try {
        const res = await fetch(`${API_BASE}/firewall/status`);
        const data = await res.json();

        currentUfwStatus = data.status;
        const badge = document.getElementById('ufw-badge');

        if (data.status === 'active') {
            badge.className = "px-3 py-1 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
            badge.innerText = "Status: Active";
        } else {
            badge.className = "px-3 py-1 rounded text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20";
            badge.innerText = "Status: Inactive";
        }

        const tbody = document.getElementById('ufw-rules-list');
        tbody.innerHTML = '';

        if (data.rules.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-slate-500">Tidak ada active rules ditemukan.</td></tr>`;
            return;
        }

        data.rules.forEach(rule => {
            tbody.innerHTML += `
                <tr class="border-b border-slate-800/50 hover:bg-slate-800/20 font-mono text-xs">
                    <td class="p-4 text-white">${rule.to}</td>
                    <td class="p-4"><span class="text-${rule.action.includes('ALLOW') ? 'emerald' : 'rose'}-400">${rule.action}</span></td>
                    <td class="p-4 text-slate-400">${rule.from}</td>
                    <td class="p-4 text-right">
                        <button onclick="deleteUfwRule('${rule.to}')" class="text-rose-400 hover:text-rose-300" title="Delete Rule"><i class="fa-solid fa-trash"></i></button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        console.error("Gagal load UFW status:", err);
    }
}

async function toggleUfwState() {
    const nextAction = currentUfwStatus === 'active' ? 'disable' : 'enable';
    const res = await fetch(`${API_BASE}/firewall/manage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command_type: 'toggle_active', action: nextAction })
    });

    if (res.ok) fetchUfwData();
    else alert("Gagal mengubah status UFW (Pastikan backend punya akses sudo tanpa password).");
}

async function addUfwRule() {
    const payload = {
        command_type: 'add_rule',
        port: document.getElementById('ufw-port').value,
        proto: document.getElementById('ufw-proto').value,
        action: document.getElementById('ufw-action').value
    };

    const res = await fetch(`${API_BASE}/firewall/manage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        document.getElementById('ufw-port').value = '';
        fetchUfwData();
    } else {
        alert("Gagal menambahkan rule UFW");
    }
}

async function deleteUfwRule(toValue) {
    const cleanPort = toValue.split('/')[0];
    const proto = toValue.includes('udp') ? 'udp' : 'tcp';

    if (!confirm(`Hapus rule untuk port ${toValue}?`)) return;

    const payload = {
        command_type: 'delete_rule',
        port: cleanPort,
        proto: proto,
        action: 'allow'
    };

    const res = await fetch(`${API_BASE}/firewall/manage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res.ok) fetchUfwData();
    else alert("Gagal menghapus rule UFW");
}

onTabChange('firewall', fetchUfwData);