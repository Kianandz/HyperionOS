<div id="section-websites" class="hidden space-y-6">
    <!-- Header & Service Controls -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h1 class="text-2xl font-bold text-white">Kelola Website & Services</h1>
            <p class="text-xs text-slate-400 mt-1">VirtualHost, Nginx & PHP-FPM Controller</p>
        </div>
        
        <div class="flex flex-wrap items-center gap-4">
            <!-- Nginx Controls -->
            <div class="flex items-center bg-slate-950 border border-slate-800 rounded-lg text-xs gap-1.5 py-1 px-3">
                <span class="text-slate-400 font-semibold mr-1">Nginx:</span>
                <button onclick="handleNginxAction('reload')" title="Reload Nginx" class="px-2 py-1 text-amber-400 hover:bg-slate-800 rounded transition font-medium">Reload</button>
                <button onclick="handleNginxAction('restart')" title="Restart Nginx" class="px-2 py-1 text-sky-400 hover:bg-slate-800 rounded transition font-medium">Restart</button>
                <button onclick="handleNginxAction('start')" title="Start Nginx" class="px-2 py-1 text-emerald-400 hover:bg-slate-800 rounded transition font-medium"><i class="fa fa-solid fa-play"></i></button>
                <button onclick="handleNginxAction('stop')" title="Stop Nginx" class="px-2 py-1 text-rose-400 hover:bg-slate-800 rounded transition font-medium"><i class="fa fa-solid fa-square"></i></button>
                <button onclick="openLogModal('nginx')" title="Nginx Logs" class="px-2 py-1 text-indigo-400 hover:bg-slate-800 rounded transition font-medium"><i class="fa fa-solid fa-file"></i></button>
            </div>

            <!-- PHP-FPM Controls -->
            <div class="flex items-center bg-slate-950 border border-slate-800 rounded-lg text-xs gap-1.5 py-1 px-3">
                <div id="badge-php-fpm" class="flex items-center gap-1.5 text-slate-400 font-semibold mr-1">
                    <span class="w-2 h-2 rounded-full bg-slate-500"></span> PHP:
                </div>
                <button onclick="handlePhpFpmAction('reload')" title="Reload PHP-FPM" class="px-2 py-1 text-amber-400 hover:bg-slate-800 rounded transition font-medium">Reload</button>
                <button onclick="handlePhpFpmAction('restart')" title="Restart PHP-FPM" class="px-2 py-1 text-sky-400 hover:bg-slate-800 rounded transition font-medium">Restart</button>
                <button onclick="handlePhpFpmAction('start')" title="Start PHP-FPM" class="px-2 py-1 text-emerald-400 hover:bg-slate-800 rounded transition font-medium"><i class="fa fa-solid fa-play"></i></button>
                <button onclick="handlePhpFpmAction('stop')" title="Stop PHP-FPM" class="px-2 py-1 text-rose-400 hover:bg-slate-800 rounded transition font-medium"><i class="fa fa-solid fa-square"></i></button>
                <button onclick="openPhpConfigModal()" title="Edit php.ini" class="px-2 py-1 text-purple-400 hover:bg-slate-800 rounded transition font-medium"><i class="fa fa-solid fa-gear"></i></button>
                <button onclick="openLogModal('php')" title="PHP Logs" class="px-2 py-1 text-indigo-400 hover:bg-slate-800 rounded transition font-medium"><i class="fa fa-solid fa-file"></i></button>
            </div>

            <button onclick="openModalWebsite()" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-2 rounded-lg text-sm transition font-medium flex items-center gap-2 px-2 ml-4">
                <i class="fa fa-solid fa-plus"></i> Tambah Website
            </button>
        </div>
    </div>

    <!-- Table Website -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table class="w-full text-left text-sm text-slate-400">
            <thead class="bg-slate-800/50 text-slate-300 text-xs uppercase">
                <tr>
                    <th class="p-4">Domain / VirtualHost</th>
                    <th class="p-4 text-center">Status</th>
                    <th class="p-4 text-right">Aksi</th>
                </tr>
            </thead>
            <tbody id="website-list-table"></tbody>
        </table>
    </div>

    <!-- MODAL WEBSITE (ORIGINAL & LENGKAP) -->
    <div id="modal-website" class="fixed inset-0 bg-black/70 backdrop-blur-sm hidden flex items-center justify-center p-4 z-50">
        <div class="bg-slate-900 w-full max-w-2xl rounded-xl p-6 space-y-4">
            <div class="flex justify-between items-center py-2">
                <h3 class="text-lg font-bold text-white" id="modal-title">Konfigurasi Domain</h3>
                
                <div class="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
                    <button id="tab-btn-simple" onclick="switchWebTab('simple')" class="px-3 py-1.5 rounded-md font-medium text-white bg-indigo-600 transition">Simple Mode</button>
                    <button id="tab-btn-advanced" onclick="switchWebTab('advanced')" class="px-3 py-1.5 rounded-md font-medium text-slate-400 hover:text-white transition">Advanced Raw Nginx</button>
                </div>
            </div>

            <input type="hidden" id="web-mode" value="simple">

            <div>
                <label class="block text-slate-400 text-xs mb-1">Domain Name</label>
                <input type="text" id="web-domain" placeholder="example.com" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white font-mono text-sm focus:outline-none focus:border-indigo-500">
            </div>

            <div id="wrapper-simple-mode" class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-slate-400 text-xs mb-1">Tipe Website</label>
                        <select id="web-type" onchange="toggleWebFields()" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white text-sm">
                            <option value="proxy">Reverse Proxy</option>
                            <option value="static">Static HTML</option>
                            <option value="php">PHP</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-slate-400 text-xs mb-1">Max Upload Size</label>
                        <input type="text" id="web-max-body" value="64M" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white text-sm">
                    </div>
                </div>

                <div id="field-port">
                    <label class="block text-slate-400 text-xs mb-1">Target Internal Port</label>
                    <input type="number" id="web-port" placeholder="3000" value="8000" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white text-sm">
                </div>

                <div id="field-root" class="hidden">
                    <label class="block text-slate-400 text-xs mb-1">Document Root Path</label>
                    <input type="text" id="web-root" value="/var/www/html" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white font-mono text-sm">
                </div>

                <div id="field-php-sock" class="hidden">
                    <label class="block text-slate-400 text-xs mb-1">PHP-FPM Unix Socket</label>
                    <input type="text" id="web-php-sock" value="/run/php-fpm/php-fpm.sock" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white font-mono text-sm">
                </div>
            </div>

            <div id="wrapper-advanced-mode" class="hidden space-y-2">
                <label class="block text-slate-400 text-xs">Raw Nginx Server Block (.conf)</label>
                <textarea id="web-raw-config" rows="10" placeholder="server { listen 80; ... }" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-emerald-400 font-mono text-xs focus:outline-none focus:border-indigo-500 leading-relaxed"></textarea>
            </div>

            <div class="flex justify-end gap-2 pt-3">
                <button onclick="closeModalWebsite()" class="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700">Batal</button>
                <button onclick="submitWebsite()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-500">Simpan Konfigurasi</button>
            </div>
        </div>
    </div>

    <!-- MODAL LOG VIEWER -->
    <div id="modal-logs" class="fixed inset-0 bg-black/70 backdrop-blur-sm hidden flex justify-center p-4 z-50 overflow-y-auto">
    <div class="bg-slate-900 w-full max-w-4xl rounded-xl p-6 border border-slate-800 shadow-2xl my-auto flex flex-col max-h-[85vh]">
        
        <!-- Header -->
        <div class="flex justify-between items-center border-b border-slate-800 pb-3 mb-4 shrink-0">
            <h3 class="text-lg font-bold text-white" id="log-modal-title">System Logs</h3>
            <button onclick="closeLogModal()" class="text-slate-400 hover:text-white"><i class="fa fa-solid fa-xmark"></i></button>
        </div>
        
        <!-- Log Content (Pasti bisa di-scroll) -->
        <pre id="log-content" class="w-full flex-1 min-h-[200px] bg-slate-950 border border-slate-800 rounded-lg p-4 text-emerald-400 font-mono text-xs overflow-y-auto whitespace-pre-wrap break-all leading-relaxed"></pre>
        
        <!-- Footer -->
        <div class="flex justify-between items-center pt-4 mt-4 border-t border-slate-800/50 shrink-0">
            <button onclick="refreshCurrentLog()" class="px-3 py-1.5 bg-slate-800 text-xs text-slate-300 rounded hover:bg-slate-700 flex items-center gap-2">
                <i class="fa fa-solid fa-rotate-right"></i> Refresh
            </button>
            <button onclick="closeLogModal()" class="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700">Tutup</button>
        </div>
        
    </div>
</div>

    <!-- MODAL CONFIG PHP (php.ini) -->
    <div id="modal-php-config" class="fixed inset-0 bg-black/70 backdrop-blur-sm hidden flex items-center justify-center p-4 z-50">
        <div class="bg-slate-900 w-full max-w-4xl rounded-xl p-6 space-y-4 border border-slate-800 shadow-2xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                <div>
                    <h3 class="text-lg font-bold text-white">PHP Configuration Editor</h3>
                    <p class="text-xs text-slate-400 font-mono mt-0.5" id="php-ini-path-label">/etc/php/php.ini</p>
                </div>
                <button onclick="closePhpConfigModal()" class="text-slate-400 hover:text-white"><i class="fa fa-solid fa-xmark"></i></button>
            </div>
            <textarea id="php-ini-content" rows="18" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-emerald-400 font-mono text-xs focus:outline-none focus:border-indigo-500 leading-relaxed"></textarea>
            <div class="flex justify-end gap-2 pt-2">
                <button onclick="closePhpConfigModal()" class="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-700">Batal</button>
                <button onclick="savePhpConfig()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-500 flex items-center gap-2">
                    <i class="fa fa-solid fa-floppy-disk"></i> Simpan & Reload
                </button>
            </div>
        </div>
    </div>
</div>