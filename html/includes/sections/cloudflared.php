<div id="section-cloudflared" class="hidden space-y-6">
    <h1 class="text-2xl font-bold text-white">Cloudflared Tunnel Configuration</h1>

    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4 max-w-xl">
        <div class="flex justify-between items-center">
            <h2 class="text-lg font-semibold text-white">Connect Connector Token</h2>
            <span id="cf-status-badge" class="px-3 py-1 rounded text-xs bg-slate-800 text-slate-400">Status: Checking...</span>
        </div>
        <p class="text-xs text-slate-400">Masukkan tunnel token dari Cloudflare Zero Trust Dashboard untuk mengaktifkan koneksi tunnel otomatis.</p>

        <div class="space-y-3">
            <textarea id="cf-token" rows="3" placeholder="eyJhIjoi..." class="w-full bg-slate-950 border border-slate-800 rounded p-3 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"></textarea>
            <button onclick="submitCloudflaredToken()" class="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-semibold transition">
                <i class="fa-solid fa-cloud-arrow-up mr-2"></i> Save & Run Tunnel
            </button>
        </div>
    </div>
</div>