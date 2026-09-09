// Event listener untuk form submission share
document.getElementById('form-share').addEventListener('submit', function(e) {
    const isGui = !document.getElementById('tab-gui').classList.contains('hidden');
    
    if (isGui) {
        const name = document.getElementById('input-share-name').value;
        const path = document.getElementById('input-share-path').value;
        const guest = document.getElementById('input-share-guest').checked ? "yes" : "no";
        const write = document.getElementById('input-share-write').checked ? "yes" : "no";
        const browse = document.getElementById('input-share-browse').checked ? "yes" : "no";
        const users = document.getElementById('input-share-users').value;
        const cmask = document.getElementById('input-share-cmask').value;
        const dmask = document.getElementById('input-share-dmask').value;
        const comment = document.getElementById('input-share-comment').value;
        const forceUser = document.getElementById('input-share-forceuser').value;
        
        let generated = `[${name}]\n    path = ${path}\n    public = ${guest}\n    guest ok = ${guest}\n    writable = ${write}\n    browseable = ${browse}\n    create mask = ${cmask}\n    directory mask = ${dmask}\n`;
        
        if(users) generated += `    valid users = ${users}\n`;
        if(comment) generated += `    comment = ${comment}\n`;
        if(forceUser) generated += `    force user = ${forceUser}\n`;
        
        document.getElementById('input-share-raw').value = generated;
    }
});

// Fungsi untuk berpindah tab antara GUI dan konfigurasi Advanced
function switchShareTab(tab) {
    const guiActive = (tab === 'gui');
    
    document.getElementById('tab-gui').classList.toggle('hidden', !guiActive);
    document.getElementById('tab-advanced').classList.toggle('hidden', guiActive);
    
    const btnGui = document.getElementById('btn-tab-gui');
    const btnAdv = document.getElementById('btn-tab-advanced');
    
    if(guiActive) {
        btnGui.className = "flex-1 py-2 text-xs font-bold rounded-lg bg-indigo-600 text-white transition-all shadow-md cursor-pointer";
        btnAdv.className = "flex-1 py-2 text-xs font-bold rounded-lg bg-transparent text-slate-400 hover:bg-slate-800 transition-all cursor-pointer";
        document.getElementById('input-share-raw').value = "";
    } else {
        btnAdv.className = "flex-1 py-2 text-xs font-bold rounded-lg bg-indigo-600 text-white transition-all shadow-md cursor-pointer";
        btnGui.className = "flex-1 py-2 text-xs font-bold rounded-lg bg-transparent text-slate-400 hover:bg-slate-800 transition-all cursor-pointer";
        
        const name = document.getElementById('input-share-name').value || "ShareName";
        const path = document.getElementById('input-share-path').value || "/path";
        const guest = document.getElementById('input-share-guest').checked ? "yes" : "no";
        const write = document.getElementById('input-share-write').checked ? "yes" : "no";
        const browse = document.getElementById('input-share-browse').checked ? "yes" : "no";
        const users = document.getElementById('input-share-users').value;
        const cmask = document.getElementById('input-share-cmask').value;
        const dmask = document.getElementById('input-share-dmask').value;
        
        let generated = `[${name}]\n    path = ${path}\n    public = ${guest}\n    guest ok = ${guest}\n    writable = ${write}\n    browseable = ${browse}\n    create mask = ${cmask}\n    directory mask = ${dmask}\n`;
        if(users) generated += `    valid users = ${users}\n`;
        
        document.getElementById('input-share-raw').value = generated;
    }
}

// Fungsi untuk membuka modal penambahan/pengeditan share
function openShareModal(shareData = null) {
    switchShareTab('gui');
    document.getElementById('smb-share-modal').classList.remove('hidden');
    
    const title = document.getElementById('modal-share-title');
    const nameInput = document.getElementById('input-share-name');
    const pathInput = document.getElementById('input-share-path');
    const usersInput = document.getElementById('input-share-users');
    const cmaskInput = document.getElementById('input-share-cmask');
    const dmaskInput = document.getElementById('input-share-dmask');
    const guestInput = document.getElementById('input-share-guest');
    const writeInput = document.getElementById('input-share-write');
    const browseInput = document.getElementById('input-share-browse');
    const rawInput = document.getElementById('input-share-raw');
    const commentInput = document.getElementById('input-share-comment');
    const forceUserInput = document.getElementById('input-share-forceuser');

    if (shareData) {
        title.innerHTML = '<i class="fa fa-edit"></i> Edit Share: ' + shareData.name;
        nameInput.value = shareData.name;
        nameInput.readOnly = true; 
        nameInput.classList.add('opacity-50');
        
        pathInput.value = shareData.path;
        usersInput.value = shareData.valid_users || "";
        cmaskInput.value = shareData.create_mask || "0755";
        dmaskInput.value = shareData.directory_mask || "0755";
        guestInput.checked = (shareData.guest_ok === 'Yes');
        writeInput.checked = (shareData.writable === 'Yes');
        browseInput.checked = (shareData.browseable === 'Yes');
        rawInput.value = shareData.raw;
        
        let commentMatch = shareData.raw.match(/comment\s*=\s*(.*)/);
        let forceMatch = shareData.raw.match(/force user\s*=\s*(.*)/);
        commentInput.value = commentMatch ? commentMatch[1].trim() : "";
        forceUserInput.value = forceMatch ? forceMatch[1].trim() : "";
    } else {
        title.innerHTML = '<i class="fa fa-folder-plus"></i> Buat Share Baru';
        document.getElementById('form-share').reset();
        nameInput.readOnly = false; 
        nameInput.classList.remove('opacity-50');
        rawInput.value = "";
        commentInput.value = "";
        forceUserInput.value = "";
    }
}

// Fungsi konfirmasi untuk menghapus share
function confirmDeleteShare(shareName) {
    SwalDark.fire({
        title: 'Hapus Share?',
        html: `Yakin mau hapus share <b class="text-rose-400">${shareName}</b>?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '<i class="fa fa-trash"></i> Ya, Hapus!',
        cancelButtonText: 'Batal',
        confirmButtonColor: '#e11d48'
    }).then((result) => {
        if (result.isConfirmed) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/files/samba/delete';
            
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'name';
            input.value = shareName;
            
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        }
    });
}