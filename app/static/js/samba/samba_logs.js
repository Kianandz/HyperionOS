// Menampilkan modal log dan melakukan fetch data ke server
async function showSambaLogs() {
    document.getElementById('smb-logs-modal').classList.remove('hidden');
    document.getElementById('smb-logs-content').textContent = "Mengambil logs dari journalctl, mohon tunggu...";
    try {
        let res = await fetch('/files/samba/logs');
        let data = await res.json();
        document.getElementById('smb-logs-content').textContent = data.logs || "Log kosong atau service belum pernah dijalankan.";
    } catch(e) {
        document.getElementById('smb-logs-content').textContent = "Gagal mengambil log dari server.";
    }
}