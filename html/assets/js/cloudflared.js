async function fetchCloudflaredStatus() {
    try {
        const res = await fetch(`${API_BASE}/cloudflared/status`);
        const data = await res.json();
        const badge = document.getElementById('cf-status-badge');
        badge.className = data.status === 'active'
            ? "px-3 py-1 rounded text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
            : "px-3 py-1 rounded text-xs bg-rose-500/10 text-rose-400 border border-rose-500/20";
        badge.innerText = `Status: ${data.status}`;
    } catch (err) {
        console.error("Gagal load Cloudflared status:", err);
    }
}

async function submitCloudflaredToken() {
    const token = document.getElementById('cf-token').value;
    const res = await fetch(`${API_BASE}/cloudflared/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token })
    });

    if (res.ok) alert("Tunnel berhasil di-submit!");
    else alert("Gagal mengaktifkan Cloudflared Tunnel.");

    fetchCloudflaredStatus();
}

onTabChange('cloudflared', fetchCloudflaredStatus);