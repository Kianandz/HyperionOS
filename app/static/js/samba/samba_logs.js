// samba_logs.js
// Display log modal and fetch data from server
async function showSambaLogs() {
    document.getElementById('smb-logs-modal').classList.remove('hidden');
    document.getElementById('smb-logs-content').textContent = "Fetching logs from journalctl, please wait...";
    try {
        let res = await fetch('/files/samba/logs');
        let data = await res.json();
        document.getElementById('smb-logs-content').textContent = data.logs || "Log is empty or service has not been run yet.";
    } catch(e) {
        document.getElementById('smb-logs-content').textContent = "Failed to fetch logs from server.";
    }
}