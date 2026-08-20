<div id="section-docker" class="hidden space-y-6">
    <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-white drop-shadow-sm">Docker Management</h1>
        <span id="docker-version" class="text-xs font-mono bg-white/10 text-slate-300 border border-white/5 px-4 py-1.5 rounded-full backdrop-blur-md">
            Version: Loading...
        </span>
    </div>

    <!-- Overview Cards ala Bento -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Card 1 -->
        <div class="bg-slate-800/40 backdrop-blur-lg border border-white/10 p-5 rounded-2xl flex justify-between items-center shadow-lg transition hover:bg-slate-800/50">
            <div>
                <p class="text-slate-400 text-sm font-medium mb-1">Containers Running</p>
                <p class="text-3xl font-bold text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.3)]" id="dk-running">0</p>
            </div>
            <i class="fa-brands fa-docker text-4xl text-emerald-500/20"></i>
        </div>
        <!-- Card 2 -->
        <div class="bg-slate-800/40 backdrop-blur-lg border border-white/10 p-5 rounded-2xl flex justify-between items-center shadow-lg transition hover:bg-slate-800/50">
            <div>
                <p class="text-slate-400 text-sm font-medium mb-1">Containers Stopped</p>
                <p class="text-3xl font-bold text-rose-400 drop-shadow-[0_0_8px_rgba(251,113,133,0.3)]" id="dk-stopped">0</p>
            </div>
            <i class="fa-solid fa-circle-stop text-4xl text-rose-500/20"></i>
        </div>
        <!-- Card 3 -->
        <div class="bg-slate-800/40 backdrop-blur-lg border border-white/10 p-5 rounded-2xl flex justify-between items-center shadow-lg transition hover:bg-slate-800/50">
            <div>
                <p class="text-slate-400 text-sm font-medium mb-1">Total Images</p>
                <p class="text-3xl font-bold text-indigo-400 drop-shadow-[0_0_8px_rgba(129,140,248,0.3)]" id="dk-images">0</p>
            </div>
            <i class="fa-solid fa-layer-group text-4xl text-indigo-500/20"></i>
        </div>
    </div>

    <!-- Table Container -->
    <div class="bg-slate-800/40 backdrop-blur-lg border border-white/10 rounded-2xl overflow-hidden shadow-lg">
        <!-- <div class="p-5 border-b border-white/10 flex justify-between items-center bg-white/5">
            <h2 class="text-lg font-semibold text-white">Containers List</h2>
            <button onclick="fetchDockerData()" class="text-sm bg-white/10 hover:bg-white/20 transition-colors text-slate-200 px-4 py-1.5 rounded-lg flex items-center gap-2">
                <i class="fa-solid fa-rotate"></i> Refresh
            </button>
        </div> -->
        <!-- Tabel tetep sama, cuma styling headernya diganti -->
        <div class="overflow-x-auto">
            <!-- <table class="w-full text-left text-sm text-slate-300">
                <thead class="bg-black/20 text-slate-400 text-xs uppercase tracking-wider">
                    <tr>
                        <th class="p-4 font-medium">ID</th>
                        <th class="p-4 font-medium">Name</th>
                        <th class="p-4 font-medium">Image</th>
                        <th class="p-4 font-medium">Status</th>
                        <th class="p-4 text-right font-medium">Actions</th>
                    </tr>
                </thead>
                <tbody id="docker-container-list" class="divide-y divide-white/5"></tbody>
            </table> -->
            <!-- Container List ala CasaOS -->
    <div class="bg-slate-800/40 backdrop-blur-lg border border-white/10 rounded-2xl p-5 shadow-lg">
        <div class="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
            <h2 class="text-lg font-semibold text-white">Installed Apps</h2>
            <div class="flex gap-2">
                <button onclick="openAppStore()" class="text-sm bg-blue-500/20 hover:bg-blue-500/30 transition-colors text-blue-400 border border-blue-500/30 px-4 py-1.5 rounded-lg flex items-center gap-2">
                    <i class="fa-solid fa-store"></i> App Store
                </button>
                <button onclick="fetchDockerData()" class="text-sm bg-white/10 hover:bg-white/20 transition-colors text-slate-200 px-4 py-1.5 rounded-lg flex items-center gap-2">
                    <i class="fa-solid fa-rotate"></i> Refresh
                </button>
            </div>
        </div>
        
        <!-- Grid list containernya di sini -->
        <div id="docker-container-list" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <!-- Hasil JS masuk ke sini -->
        </div>
    </div>
        </div>
    </div>
</div>

<!-- Modal Detail Docker dengan Tabs -->
<div id="docker-modal" onclick="if(event.target === this) closeDockerModal()" class="hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center transition-opacity duration-300">
    <div class="bg-slate-800 border border-white/10 rounded-2xl w-full max-w-lg p-6 shadow-2xl transform scale-95 transition-transform duration-300">
        
        <!-- Header Modal -->
        <div class="flex justify-between items-start mb-4 border-b border-white/10 pb-3">
            <h3 class="text-xl font-bold text-white flex items-center gap-3">
                <i class="fa-brands fa-docker text-blue-400"></i>
                <span id="modal-c-name">Loading...</span>
            </h3>
            <button onclick="closeDockerModal()" class="text-slate-400 hover:text-white transition text-2xl font-bold leading-none">&times;</button>
        </div>

        <!-- Menu Tabs -->
        <div class="flex gap-4 mb-4 border-b border-white/10 pb-2">
            <button onclick="showTab('info')" class="text-sm font-medium text-blue-400 border-b border-blue-400 pb-1" id="tab-btn-info">Info</button>
            <button onclick="showTab('env')" class="text-sm font-medium text-slate-400 hover:text-slate-200 pb-1" id="tab-btn-env">Env</button>
            <button onclick="showTab('volumes')" class="text-sm font-medium text-slate-400 hover:text-slate-200 pb-1" id="tab-btn-volumes">Volumes</button>
        </div>

        <!-- Konten Tabs yang bakal gonta-ganti -->
        <div id="modal-tab-content" class="min-h-[150px] max-h-[300px] overflow-y-auto text-sm text-slate-300 mb-6">
            <!-- Isi di-inject dari JS -->
        </div>

        <!-- Tombol Aksi Bawah -->
        <div class="flex gap-3" id="modal-actions-container">
            <!-- Di-inject via JS -->
        </div>
    </div>
</div>

<!-- Modal App Store -->
<div id="appstore-modal" onclick="if(event.target === this) closeAppStore()" class="hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center transition-opacity duration-300">
    <div class="bg-slate-800 border border-white/10 rounded-2xl w-full max-w-4xl p-6 shadow-2xl h-[80vh] flex flex-col transform scale-95 transition-transform duration-300">
        
        <div class="flex justify-between items-start mb-4 border-b border-white/10 pb-3">
            <h3 class="text-xl font-bold text-white flex items-center gap-3">
                <i class="fa-solid fa-store text-emerald-400"></i> App Store
            </h3>
            <button onclick="closeAppStore()" class="text-slate-400 hover:text-white transition text-2xl font-bold leading-none">&times;</button>
        </div>

        <!-- List App Store -->
        <div id="appstore-list" class="grid grid-cols-2 md:grid-cols-4 gap-4 overflow-y-auto pr-2 pb-4">
            <!-- Hasil JS masuk ke sini -->
        </div>
    </div>
</div>