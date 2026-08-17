<div id="section-docker" class="hidden space-y-6">
    <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-white">Docker Management</h1>
        <span id="docker-version" class="text-xs font-mono bg-slate-800 text-slate-400 border border-slate-700 px-3 py-1 rounded">
            Version: Loading...
        </span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex justify-between items-center">
            <div>
                <p class="text-slate-400 text-sm">Containers Running</p>
                <p class="text-2xl font-bold text-emerald-400" id="dk-running">0</p>
            </div>
            <i class="fa-brands fa-docker text-3xl text-emerald-500/20"></i>
        </div>
        <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex justify-between items-center">
            <div>
                <p class="text-slate-400 text-sm">Containers Stopped</p>
                <p class="text-2xl font-bold text-rose-400" id="dk-stopped">0</p>
            </div>
            <i class="fa-solid fa-circle-stop text-3xl text-rose-500/20"></i>
        </div>
        <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl flex justify-between items-center">
            <div>
                <p class="text-slate-400 text-sm">Total Images</p>
                <p class="text-2xl font-bold text-indigo-400" id="dk-images">0</p>
            </div>
            <i class="fa-solid fa-layer-group text-3xl text-indigo-500/20"></i>
        </div>
    </div>

    <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div class="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 class="text-lg font-semibold text-white">Containers List</h2>
            <button onclick="fetchDockerData()" class="text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded">
                <i class="fa-solid fa-rotate mr-1"></i> Refresh
            </button>
        </div>
        <table class="w-full text-left text-sm text-slate-400">
            <thead class="bg-slate-800/50 text-slate-300 text-xs uppercase">
                <tr>
                    <th class="p-4">ID</th>
                    <th class="p-4">Name</th>
                    <th class="p-4">Image</th>
                    <th class="p-4">Status</th>
                    <th class="p-4 text-right">Actions</th>
                </tr>
            </thead>
            <tbody id="docker-container-list"></tbody>
        </table>
    </div>
</div>