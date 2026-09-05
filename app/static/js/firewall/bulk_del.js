function toggleSelectAll(source) {
    const checkboxes = document.querySelectorAll('.rule-checkbox');
    checkboxes.forEach(cb => cb.checked = source.checked);
    updateBulkBtn();
}

function updateBulkBtn() {
    const checkedBoxes = document.querySelectorAll('.rule-checkbox:checked');
    const btn = document.getElementById('bulk-delete-btn');
    const countSpan = document.getElementById('selected-count');
    
    if (checkedBoxes.length > 0) {
        btn.classList.remove('hidden');
        countSpan.textContent = checkedBoxes.length;
    } else {
        btn.classList.add('hidden');
    }
}

function deleteSelectedRules() {
    const checkedBoxes = document.querySelectorAll('.rule-checkbox:checked');
    if (checkedBoxes.length === 0) return;

    Swal.fire({
        title: 'Sikat Semua?',
        text: `Lu yakin mau hapus ${checkedBoxes.length} baris rule ini?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#334155',
        confirmButtonText: 'Ya, Hapus!',
        background: '#0f172a',
        color: '#fff'
    }).then(async (result) => {
        if (result.isConfirmed) {
            
            Swal.fire({
                title: 'Lagi ngehapus...',
                allowOutsideClick: false,
                background: '#0f172a',
                color: '#fff',
                didOpen: () => Swal.showLoading()
            });

            try {
                // Pake Set biar ngga ada request duplikat buat port yang sama
                const uniqueRules = new Set();
                
                checkedBoxes.forEach(cb => {
                    const action = cb.dataset.action;
                    const cleanPort = cb.dataset.port.replace(" (v6)", ""); 
                    uniqueRules.add(`${action}|${cleanPort}`);
                });

                for (const rule of uniqueRules) {
                    const [action, port] = rule.split('|');
                    const data = new FormData();
                    data.append('command_type', 'delete_rule');
                    data.append('action', action);
                    data.append('port', port);

                    const res = await fetch('/firewall/action', { method: 'POST', body: data });
                    // Kalo dapet 400 karena rule udah beneran kehapus, kita cuekin aja (skip)
                    if (!res.ok) console.warn("Skipped or already deleted:", port);
                }
                
                htmx.trigger("body", "reloadRules");
                
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'success',
                    title: `Proses hapus rule kelar!`,
                    showConfirmButton: false,
                    timer: 2000,
                    background: '#0f172a',
                    color: '#fff'
                });
                
            } catch (err) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error jir',
                    text: 'Ada rule yang gagal dihapus, cek log server.',
                    background: '#0f172a',
                    color: '#fff'
                });
            }
        }
    });
}