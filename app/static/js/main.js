// Function buat ganti tab di halaman Settings (Jinja2 Rendered)
function switchSettingTab(tabName) {
    const panels = document.querySelectorAll('.setting-panel');
    panels.forEach(panel => panel.classList.add('hidden'));

    const buttons = document.querySelectorAll('.setting-tab-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active', 'text-slate-300', 'bg-slate-800/50');
        btn.classList.add('text-slate-400');
    });

    const targetPanel = document.getElementById(`setting-panel-${tabName}`);
    if (targetPanel) targetPanel.classList.remove('hidden');

    const activeBtn = document.getElementById(`tab-btn-${tabName}`);
    if (activeBtn) {
        activeBtn.classList.add('active', 'text-slate-300', 'bg-slate-800/50');
        activeBtn.classList.remove('text-slate-400');
    }
}

// Save Local Preferences (Polling & Theme)
function saveGeneralUI() {
    const rate = document.getElementById('cfg-interval')?.value || '5000';
    const theme = document.getElementById('cfg-theme')?.value || 'dark';

    localStorage.setItem('REFRESH_RATE', rate);
    localStorage.setItem('HYPERION_THEME', theme);

    alert("Preferensi UI berhasil disimpan!");
    location.reload();
}

// Preset Quick Rule UFW
function setPreset(port, proto, action) {
    const elPort = document.getElementById('ufw-port');
    const elProto = document.getElementById('ufw-proto');
    const elAction = document.getElementById('ufw-action');

    if (elPort) elPort.value = port;
    if (elProto) elProto.value = proto;
    if (elAction) elAction.value = action;
}