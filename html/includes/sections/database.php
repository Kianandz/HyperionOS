<div id="section-database" class="hidden space-y-6">
    <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-white">Kelola Database Remote</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4 md:col-span-1">
            <h2 class="text-lg font-semibold text-white">Connect Remote Server</h2>
            <div class="space-y-3 text-sm">
                <div>
                    <label class="block text-slate-400 mb-1">Database Engine</label>
                    <select id="db-type" onchange="updateDefaultPort()" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white">
                        <option value="mysql">MySQL / MariaDB</option>
                        <option value="postgres">PostgreSQL</option>
                        <option value="mssql">SQL Server (MSSQL)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-slate-400 mb-1">Host / IP Remote</label>
                    <input type="text" id="db-host" placeholder="192.168.1.100" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white">
                </div>
                <div>
                    <label class="block text-slate-400 mb-1">Port</label>
                    <input type="number" id="db-port" value="3306" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white">
                </div>
                <div>
                    <label class="block text-slate-400 mb-1">Username</label>
                    <input type="text" id="db-user" placeholder="root" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white">
                </div>
                <div>
                    <label class="block text-slate-400 mb-1">Password</label>
                    <input type="password" id="db-pass" class="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white">
                </div>
                <button onclick="connectDatabase()" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded font-semibold transition mt-2">
                    <i class="fa fa-solid fa-plug mr-2"></i> Test & Load Databases
                </button>
            </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4 md:col-span-2">
            <h2 class="text-lg font-semibold text-white">Daftar Database</h2>
            <div id="db-status-msg" class="text-sm text-slate-500 italic">Belum terkoneksi ke server mana pun.</div>
            <ul id="db-list" class="space-y-2 font-mono text-sm hidden"></ul>
        </div>

        <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4 md:col-span-3 hidden" id="table-explorer-section">
            <h2 class="text-lg font-semibold text-white">
                <i class="fa fa-table mr-2 text-indigo-400"></i> Explorer: <span id="active-db-label" class="text-emerald-400"></span>
            </h2>
            
            <!-- Area List Tabel -->
            <div id="table-list-gui" class="flex flex-wrap gap-2 mb-4">
                <span class="text-sm text-slate-500 italic">Memuat tabel...</span>
            </div>
        </div>
    </div>
    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4 md:col-span-3 mt-4">
    <div class="flex justify-between items-center hidden">
        <h2 class="text-lg font-semibold text-white"><i class="fa fa-terminal text-indigo-400 mr-2"></i>SQL Console</h2>
        <input type="text" id="selected-db" placeholder="Database Name" class="bg-slate-950 border border-slate-800 rounded px-3 py-1 text-sm text-indigo-300 font-mono" />
    </div>

    <textarea id="sql-query" rows="3" class="w-full bg-slate-950 border border-slate-800 rounded p-3 text-emerald-400 font-mono text-sm focus:outline-none focus:border-indigo-500 hidden" placeholder="SELECT * FROM users LIMIT 10;"></textarea>

    <div class="flex justify-between items-center hidden">
        <button onclick="runSqlQuery()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded font-semibold text-sm transition flex items-center">
            <i class="fa fa-play mr-2"></i> Execute Query
        </button>
        <span id="query-status" class="text-xs text-slate-400 font-mono"></span>
    </div>

    <!-- Output Data Table -->
    <div id="query-result-container" class="overflow-x-auto hidden border border-slate-800 rounded overflow-y-auto h-[50vh]">
        <table class="w-full text-left text-sm text-slate-300 font-mono">
            <thead id="query-table-head" class="sticky top-0 z-10 bg-slate-950 text-indigo-400 uppercase text-xs border-b border-slate-800"></thead>
            <tbody id="query-table-body" class="divide-y divide-slate-800 bg-slate-900/50"></tbody>
        </table>
    </div>
</div>
</div>