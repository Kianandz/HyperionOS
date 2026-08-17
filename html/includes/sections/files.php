<div id="section-files" class="hidden space-y-6">
    <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-white">File Manager</h1>
        <span id="fm-current-path" class="font-mono text-sm text-indigo-400 bg-slate-900 border border-slate-800 px-3 py-1 rounded">/</span>
    </div>

    <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table class="w-full text-left text-sm text-slate-400">
            <thead class="bg-slate-800/50 text-slate-300 text-xs uppercase">
                <tr>
                    <th class="p-4">Nama File / Folder</th>
                    <th class="p-4">Tipe</th>
                    <th class="p-4">Ukuran</th>
                    <th class="p-4 text-right">Aksi</th>
                </tr>
            </thead>
            <tbody id="file-manager-list"></tbody>
        </table>
    </div>
</div>