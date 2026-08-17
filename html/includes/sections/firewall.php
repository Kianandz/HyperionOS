<div id="section-firewall" class="hidden space-y-6">
    <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-white">Firewall Management (UFW)</h1>
        <div class="flex items-center space-x-3">
            <span id="ufw-badge" class="px-3 py-1 rounded text-xs font-semibold bg-slate-800 text-slate-400">Status: Checking...</span>
            <button onclick="toggleUfwState()" id="ufw-toggle-btn" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded text-sm transition">Toggle UFW</button>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4 md:col-span-1">
            <h2 class="text-lg font-semibold text-white">Tambah Rule Port</h2>
            <div class="space-y-3 text-sm">
                <div>
                    <label class="block text-slate-400 mb-1">Aksi</label>
                    <select id="ufw-action" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white">
                        <option value="allow">Allow (Izinkan)</option>
                        <option value="deny">Deny (Blokir)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-slate-400 mb-1">Nomor Port</label>
                    <input type="number" id="ufw-port" placeholder="80 atau 443" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white">
                </div>
                <div>
                    <label class="block text-slate-400 mb-1">Protocol</label>
                    <select id="ufw-proto" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white">
                        <option value="tcp">TCP</option>
                        <option value="udp">UDP</option>
                    </select>
                </div>
                <button onclick="addUfwRule()" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded font-semibold transition mt-2">
                    <i class="fa-solid fa-shield-plus mr-2"></i> Tambah Rule
                </button>
            </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden md:col-span-2">
            <div class="p-4 border-b border-slate-800 flex justify-between items-center">
                <h2 class="text-lg font-semibold text-white">Active Rules</h2>
                <button onclick="fetchUfwData()" class="text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded">
                    <i class="fa-solid fa-rotate mr-1"></i> Refresh
                </button>
            </div>
            <table class="w-full text-left text-sm text-slate-400">
                <thead class="bg-slate-800/50 text-slate-300 text-xs uppercase">
                    <tr>
                        <th class="p-4">To (Port/Service)</th>
                        <th class="p-4">Action</th>
                        <th class="p-4">From</th>
                        <th class="p-4 text-right">Aksi</th>
                    </tr>
                </thead>
                <tbody id="ufw-rules-list"></tbody>
            </table>
        </div>
    </div>
</div>