// bulk_del_2.js
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
        title: 'Delete Selected Rules?',
        text: `Are you sure you want to delete these ${checkedBoxes.length} selected rules?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#334155',
        confirmButtonText: 'Yes, Delete!',
        background: '#0f172a',
        color: '#fff'
    }).then(async (result) => {
        if (result.isConfirmed) {
            
            Swal.fire({
                title: 'Deleting...',
                allowOutsideClick: false,
                background: '#0f172a',
                color: '#fff',
                didOpen: () => Swal.showLoading()
            });

            try {
                // Use a Set to avoid duplicate requests for the same port
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
                    // If 400 is returned because rule is already deleted, skip it
                    if (!res.ok) console.warn("Skipped or already deleted:", port);
                }
                
                htmx.trigger("body", "reloadRules");
                
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'success',
                    title: `Rule deletion process completed!`,
                    showConfirmButton: false,
                    timer: 2000,
                    background: '#0f172a',
                    color: '#fff'
                });
                
            } catch (err) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Failed to delete some rules. Check server logs.',
                    background: '#0f172a',
                    color: '#fff'
                });
            }
        }
    });
}