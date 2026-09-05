let currentDockerData = null;

async function loadAppStoreData() {
    const container = document.getElementById('appstore-container');
    if (container.dataset.loaded === "true") return;

    try {
        const response = await fetch('https://raw.githubusercontent.com/Lissy93/portainer-templates/main/templates.json'); 
        const data = await response.json();
        const apps = data.templates.filter(app => app.type === 1);
        
        let html = '';
        apps.forEach(app => {
            const iconUrl = app.logo || 'https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/docker.png';
            let defaultPort = 80;
            let containerPort = 80;
            if (app.ports && app.ports.length > 0) {
                const portParts = app.ports[0].split(':');
                if (portParts.length > 1) {
                    defaultPort = portParts[0];
                    containerPort = portParts[1].split('/')[0];
                }
            }
            const appTitle = app.title.replace(/'/g, "\\'");
            
            html += `
            <div class="app-card h-fit bg-slate-950 border border-white/5 rounded-xl p-4 flex flex-col items-center text-center hover:border-white/20 transition-all shadow-md">
                <div class="w-16 h-16 mb-3 p-1 bg-white/5 rounded-2xl flex items-center justify-center">
                    <img src="${iconUrl}" class="w-full h-full object-contain drop-shadow-md" onerror="this.src='https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/docker.png'">
                </div>
                <h4 class="text-white font-bold w-full truncate" title="${app.title}">${app.title}</h4>
                <p class="text-xs text-slate-400 mb-4 line-clamp-2 w-full h-8" title="${app.description}">${app.description}</p>
                <button onclick="installApp('${app.image}', '${appTitle}', ${defaultPort}, ${containerPort}, this)" class="w-full mt-auto py-2 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600 hover:text-white rounded-lg text-sm font-medium transition-all cursor-pointer">
                    Install
                </button>
            </div>`;
        });
        
        container.innerHTML = html;
        container.dataset.loaded = "true";
    } catch (error) {
        console.error("Gagal load app store:", error);
        container.innerHTML = `<div class="col-span-full text-center text-rose-500 py-10">Gagal narik data App Store eksternal. Cek koneksi lu, cok.</div>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('appstore-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('#appstore-container .app-card');
            cards.forEach(card => {
                const title = card.querySelector('h4')?.textContent.toLowerCase() || "";
                const desc = card.querySelector('p')?.textContent.toLowerCase() || "";
                card.style.display = (title.includes(searchTerm) || desc.includes(searchTerm)) ? 'flex' : 'none';
            });
        });
    }
});

async function installApp(imageName, appTitle, defaultPort, containerPort, btn) {
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fa fa-solid fa-circle-notch fa-spin mr-1"></i> Installing...`;
    btn.disabled = true;
    btn.classList.remove('hover:bg-indigo-600', 'hover:text-white', 'cursor-pointer');
    btn.classList.add('opacity-70', 'cursor-wait');

    try {
        const formData = new FormData();
        formData.append('image', imageName);
        formData.append('title', appTitle);
        formData.append('default_port', defaultPort);
        formData.append('container_port', containerPort);

        const response = await fetch('/docker/api/install', { method: 'POST', body: formData });
        const result = await response.json();

        if (response.ok && result.status === 'success') {
            btn.innerHTML = `<i class="fa fa-solid fa-check mr-1"></i> Installed (Port: ${result.port})`;
            btn.classList.remove('bg-indigo-600/20', 'text-indigo-400', 'cursor-wait', 'opacity-70');
            btn.classList.add('bg-emerald-500/20', 'text-emerald-400');
            setTimeout(() => window.location.reload(), 2000); 
        } else {
            throw new Error(result.message || "Gagal install dari server");
        }
    } catch (error) {
        btn.innerHTML = originalText;
        btn.disabled = false;
        btn.classList.remove('opacity-70', 'cursor-wait');
        btn.classList.add('hover:bg-indigo-600', 'hover:text-white', 'cursor-pointer');
        Swal.fire({ icon: 'error', title: 'Install Gagal!', text: error.message, background: '#0f172a', color: '#f8fafc', confirmButtonColor: '#4f46e5' });
    }
}

async function openAppStore() {
    document.getElementById('appstore-modal').classList.remove('hidden');
    await loadAppStoreData();
}

function closeAppStore() {
    document.getElementById('appstore-modal').classList.add('hidden');
    const searchInput = document.getElementById('appstore-search');
    if (searchInput) {
        searchInput.value = '';
        document.querySelectorAll('#appstore-container .app-card').forEach(card => card.style.display = 'flex');
    }
}