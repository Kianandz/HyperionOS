<div id="section-home" class="space-y-6">
    <div class="flex justify-between items-center">
        <div>
            <h1 class="text-2xl font-bold text-white">System Overview</h1>
            <p class="text-xs text-slate-400 mt-0.5" id="val-hostname">Host: Loading...</p>
        </div>
        <span class="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Server Live
        </span>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-slate-900/60 border border-slate-800/80 p-3 rounded-lg">
            <span class="text-xs text-slate-400 block">Uptime</span>
            <span class="text-sm font-semibold font-mono text-slate-200" id="val-uptime">-</span>
        </div>
        <div class="bg-slate-900/60 border border-slate-800/80 p-3 rounded-lg">
            <span class="text-xs text-slate-400 block">OS Platform</span>
            <span class="text-sm font-semibold text-slate-200" id="val-os">-</span>
        </div>
        <div class="bg-slate-900/60 border border-slate-800/80 p-3 rounded-lg">
            <span class="text-xs text-slate-400 block">CPU Cores</span>
            <span class="text-sm font-semibold text-slate-200" id="val-cores">- Cores</span>
        </div>
        <div class="bg-slate-900/60 border border-slate-800/80 p-3 rounded-lg">
            <span class="text-xs text-slate-400 block">Active Processes</span>
            <span class="text-sm font-semibold text-slate-200" id="val-processes">- Tasks</span>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
            <div class="flex justify-between items-center">
                <div class="text-slate-400 text-sm">CPU Usage</div>
                <div class="text-2xl font-bold text-indigo-400" id="val-cpu">0%</div>
            </div>
            <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div id="bar-cpu" class="bg-indigo-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
            </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
            <div class="flex justify-between items-start">
                <div>
                    <div class="text-slate-400 text-sm">RAM Usage</div>
                    <div class="text-2xl font-bold text-blue-400" id="val-ram">0 GB</div>
                </div>
                <span class="text-xs text-slate-500 font-mono" id="val-ram-percent">0% used</span>
            </div>
            <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div id="bar-ram" class="bg-blue-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
            </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
            <div class="text-slate-400 text-sm mb-1">Download Speed</div>
            <div class="text-3xl font-bold text-emerald-400" id="val-net-down">0 KB/s</div>
        </div>

        <div class="bg-slate-900 border border-slate-800 p-5 rounded-xl">
            <div class="text-slate-400 text-sm mb-1">Upload Speed</div>
            <div class="text-3xl font-bold text-purple-400" id="val-net-up">0 KB/s</div>
        </div>
    </div>

    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
        <h2 class="text-lg font-semibold text-white">Disk Storage</h2>
        <div id="disk-list" class="space-y-4"></div>
    </div>
</div>