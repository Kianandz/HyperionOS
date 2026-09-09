// Fungsi membuka modal user
async function openUserModal() {
    document.getElementById('smb-user-modal').classList.remove('hidden');
    switchUserTab('list');
    await loadSambaUsers();
}

// Fungsi berpindah tab antara List dan Add User
function switchUserTab(tab) {
    const isList = (tab === 'list');
    document.getElementById('tab-user-list').classList.toggle('hidden', !isList);
    document.getElementById('tab-user-add').classList.toggle('hidden', isList);
    
    document.getElementById('btn-user-list').className = isList ? "flex-1 py-2 text-xs font-bold rounded-lg bg-emerald-600 text-white shadow-md cursor-pointer" : "flex-1 py-2 text-xs font-bold rounded-lg bg-transparent text-slate-400 hover:bg-slate-800 cursor-pointer";
    document.getElementById('btn-user-add').className = !isList ? "flex-1 py-2 text-xs font-bold rounded-lg bg-emerald-600 text-white shadow-md cursor-pointer" : "flex-1 py-2 text-xs font-bold rounded-lg bg-transparent text-slate-400 hover:bg-slate-800 cursor-pointer";
}

// Fungsi memuat daftar user dari server
async function loadSambaUsers() {
    const container = document.getElementById('user-list-container');
    container.innerHTML = '<div class="text-center text-slate-500 text-xs py-4"><i class="fa fa-spinner fa-spin mr-2"></i>Memuat...</div>';
    try {
        let res = await fetch('/files/samba/api/users');
        let data = await res.json();
        if (!data.users || data.users.length === 0) {
            container.innerHTML = '<div class="text-slate-500 text-xs text-center py-4">Belum ada user Samba.</div>';
            return;
        }
        
        let html = '';
        data.users.forEach(u => {
            html += `
            <div class="flex justify-between items-center bg-slate-950/80 p-3 rounded-xl border border-slate-700/50 hover:border-emerald-500/30 transition-colors">
                <span class="text-emerald-400 font-bold text-sm"><i class="fa fa-user-circle mr-2"></i>${u}</span>
                <div class="flex gap-2">
                    <button type="button" onclick="editUserPassword('${u}')" class="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg text-[10px] font-bold cursor-pointer">
                        <i class="fa fa-key"></i> Edit
                    </button>
                    <button type="button" onclick="confirmDeleteUser('${u}')" class="bg-rose-900/30 hover:bg-rose-600 text-rose-400 hover:text-white px-3 py-1.5 rounded-lg text-[10px] font-bold transition-colors cursor-pointer">
                        <i class="fa fa-trash"></i>
                    </button>
                </div>
            </div>`;
        });
        container.innerHTML = html;
    } catch(e) {
        container.innerHTML = '<div class="text-rose-500 text-xs text-center py-4">Gagal meload user.</div>';
    }
}

// Mengedit password user yang sudah ada
function editUserPassword(username) {
    switchUserTab('add');
    document.getElementById('input-username').value = username;
}

// Konfirmasi pencabutan akses user
function confirmDeleteUser(username) {
    SwalDark.fire({
        title: 'Hapus Akses User?',
        html: `Cabut akses Samba untuk user <b class="text-rose-400">${username}</b>?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '<i class="fa fa-trash"></i> Ya, Cabut!',
        cancelButtonText: 'Batal',
        confirmButtonColor: '#e11d48'
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/files/samba/user/delete';
            
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'username';
            input.value = username;
            
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        }
    });
}