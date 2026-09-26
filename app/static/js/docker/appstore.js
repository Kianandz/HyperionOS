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
            <div class="app-card bg-slate-950 border border-white/5 hover:bg-slate-800/80 rounded-xl p-3 md:p-4 flex items-center gap-3 transition-all hover:shadow-lg cursor-pointer group">
                
                <!-- Icon -->
                <div class="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center shrink-0 p-1.5 overflow-hidden">
                    <img src="${iconUrl}" class="w-full h-full object-contain" onerror="this.src='https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/docker.png'">
                </div>
                
                <!-- Info text (min-w-0 dan overflow-hidden memastikan teks tidak bocor) -->
                <div class="flex-1 min-w-0 overflow-hidden pr-2">
                    <h4 class="text-white font-semibold text-sm truncate" title="${app.title}">
                        ${app.title}
                    </h4>
                    <!-- Deskripsi dibatasi maksimal 2 baris agar rapi -->
                    <p class="text-[11px] text-slate-400 mt-1 line-clamp-2 whitespace-normal break-words leading-snug w-full" title="${app.description}">${app.description}</p>
                </div>
                
                <!-- Button Install -->
                <button onclick="installApp('${app.image}', '${appTitle}', ${defaultPort}, ${containerPort}, this)" class="shrink-0 px-3 py-1.5 bg-indigo-500/10 text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white rounded-lg text-xs font-semibold transition-all">
                    Install
                </button>
                
            </div>`;
        });
        
        container.innerHTML = html;
        container.dataset.loaded = "true";
    } catch (error) {
        console.error("Failed to load app store:", error);
        container.innerHTML = `<div class="col-span-full text-center text-rose-500 py-10">Failed to fetch external App Store data. Check your connection.</div>`;
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
            throw new Error(result.message || "Failed to install from server");
        }
    } catch (error) {
        btn.innerHTML = originalText;
        btn.disabled = false;
        btn.classList.remove('opacity-70', 'cursor-wait');
        btn.classList.add('hover:bg-indigo-600', 'hover:text-white', 'cursor-pointer');
        Swal.fire({ icon: 'error', title: 'Installation Failed!', text: error.message, background: '#0f172a', color: '#f8fafc', confirmButtonColor: '#4f46e5' });
    }
}

// async function openAppStore() {
//     document.getElementById('appstore-modal').classList.remove('hidden');
//     await loadAppStoreData();
// }

function closeAppStore() {
    document.getElementById('appstore-modal').classList.add('hidden');
    const searchInput = document.getElementById('appstore-search');
    if (searchInput) {
        searchInput.value = '';
        document.querySelectorAll('#appstore-container .app-card').forEach(card => card.style.display = 'flex');
    }
}