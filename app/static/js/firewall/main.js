// Modal Handlers
function openModal(id) {
    const modal = document.getElementById(id);
    modal.classList.remove('hidden');
}

function closeModal(id) {
    const modal = document.getElementById(id);
    modal.classList.add('hidden');
}

function setFwPreset(port, proto, action) {
    document.getElementById('fw-port').value = port;
    document.getElementById('fw-proto').value = proto;
    document.getElementById('fw-action').value = action;
}

// POST via Fetch API biar nggak reload
async function apiCall(data, successMsg) {
    try {
        const formData = new FormData();
        for (const key in data) formData.append(key, data[key]);

        const res = await fetch('/firewall/action', {
            method: 'POST',
            body: formData
        });
        
        const json = await res.json();
        
        if (!res.ok || json.status === 'error') throw new Error(json.message);
        
        // Trigger HTMX buat refresh tabel doang
        htmx.trigger("body", "reloadRules");
        
        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: 'success',
            title: successMsg,
            showConfirmButton: false,
            timer: 2000,
            background: '#0f172a',
            color: '#fff'
        });
    } catch (err) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: err.message,
            background: '#0f172a',
            color: '#fff'
        });
    }
}

// Tambah Rule dari form Modal
function submitRule(e) {
    e.preventDefault();
    const form = e.target;
    const data = {
        command_type: form.command_type.value,
        port: form.port.value,
        proto: form.proto.value,
        action: form.action.value
    };
    
    apiCall(data, 'Rule berhasil ditambahkan!');
    closeModal('addRuleModal');
    form.reset();
}

// Hapus Rule pake konfirmasi
function deleteRule(action, port) {
    // Bersihin embel-embel (v6) biar UFW ngga bingung
    const cleanPort = port.replace(" (v6)", "");
    
    Swal.fire({
        title: 'Hapus Rule?',
        text: `Lu yakin mau hapus rule untuk ${cleanPort}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#334155',
        confirmButtonText: 'Ya, Hapus!',
        background: '#0f172a',
        color: '#fff'
    }).then((result) => {
        if (result.isConfirmed) {
            apiCall({
                command_type: 'delete_rule',
                action: action,
                port: cleanPort
            }, 'Rule berhasil dihapus!');
        }
    });
}

// Toggle UFW ON/OFF
function toggleUFW(currentStatus) {
    const action = currentStatus === 'active' ? 'disable' : 'enable';
    Swal.fire({
        title: `${action.toUpperCase()} UFW?`,
        text: `Ini bakal ngubah status firewall server lu.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#6366f1',
        cancelButtonColor: '#334155',
        confirmButtonText: 'Lanjutkan',
        background: '#0f172a',
        color: '#fff'
    }).then((result) => {
        if (result.isConfirmed) {
            apiCall({
                command_type: 'toggle_active',
                action: action
            }, `UFW ${action}d successfully!`).then(() => {
                setTimeout(() => location.reload(), 1000); // Reload bentar biar header status ganti
            });
        }
    });
}