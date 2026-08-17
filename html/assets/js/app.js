const API_BASE = 'http://localhost:8000/api';

const tabCallbacks = {};

function onTabChange(tabName, callback) {
    tabCallbacks[tabName] = callback;
}

function switchTab(tabName) {
    const sections = ['home', 'websites', 'database', 'docker', 'firewall', 'files', 'cloudflared', 'settings'];
    
    sections.forEach(sec => {
        const el = document.getElementById(`section-${sec}`);
        if (el) el.classList.add('hidden');
    });

    const activeEl = document.getElementById(`section-${tabName}`);
    if (activeEl) activeEl.classList.remove('hidden');

    if (tabCallbacks[tabName]) {
        tabCallbacks[tabName]();
    }
}

document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem("hyperion_user");
    window.location.reload()
});