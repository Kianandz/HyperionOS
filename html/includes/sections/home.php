<div id="section-home" class="hidden space-y-6">

    <!-- Header & Status Controls -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h1 class="text-2xl font-bold text-white">System Overview</h1>
            <p class="text-xs text-slate-400 mt-1">Server Monitor & Status</p>
        </div>
        
        <div class="flex flex-wrap items-center gap-4">
            <!-- Status Badge -->
            <div class="flex items-center bg-slate-950 border border-slate-800 rounded-lg text-xs gap-2 py-1 px-3">
                <span class="relative flex h-2 w-2">
                    <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50"></span>
                    <span class="relative h-2 w-2 rounded-full bg-emerald-400"></span>
                </span>
                <span class="text-slate-400 font-semibold mr-1">Status:</span>
                <span class="text-emerald-400 font-bold uppercase tracking-widest text-[10px] mt-0.5">Online</span>
            </div>
        </div>
    </div>

    <!-- Grid Container -->
    <div class="grid grid-cols-1 gap-4 md:grid-cols-4">

        <!-- =========================
             HOSTNAME
        ========================== -->
        <div class="md:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div class="flex h-full flex-col justify-center">
                <p class="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                    Hostname
                </p>
                <p id="val-hostname" class="mt-1.5 flex items-center gap-1.5 font-mono text-xs text-slate-300 truncate">
                    <svg class="h-4 w-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>
                    </svg>
                    Loading...
                </p>
            </div>
        </div>

        <!-- =========================
             CPU
        ========================== -->
        <div class="md:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div class="flex h-full flex-col justify-center">
                <p class="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                    CPU Usage
                </p>
                <div class="flex items-end justify-between gap-4">
                    <p id="val-cpu" class="font-mono text-4xl font-semibold tracking-tight text-white">
                        0%
                    </p>
                    <div class="mb-1 h-1.5 w-full max-w-xs overflow-hidden rounded-full bg-slate-800">
                        <div id="bar-cpu" class="h-full rounded-full bg-indigo-500 transition-[width] duration-700 ease-out" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- =========================
             MEMORY
        ========================== -->
        <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div class="flex h-full items-center justify-between gap-6">
                <div>
                    <p class="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                        Memory
                    </p>
                    <p id="val-ram" class="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                        0 / 0 GB
                    </p>
                </div>
                <div class="shrink-0">
                    <div id="val-ram-percent" class="rounded-lg bg-indigo-500/[0.08] px-3 py-2 font-mono text-xs font-semibold text-indigo-400 ring-1 ring-indigo-400/10">
                        0% used
                    </div>
                </div>
            </div>
            <div class="mt-5 h-1.5 overflow-hidden rounded-full bg-slate-800">
                <div id="bar-ram" class="h-full rounded-full bg-indigo-500 transition-[width] duration-700 ease-out" style="width: 0%"></div>
            </div>
        </div>

        <!-- =========================
             STORAGE
        ========================== -->
        <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div class="mb-4 flex items-center gap-2">
                <svg class="h-4 w-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/>
                </svg>
                <span class="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                    Storage Volumes
                </span>
            </div>
            <div id="disk-list" class="space-y-4"></div>
        </div>

        <!-- =========================
             SMALL STATS
        ========================== -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl px-5 py-5">
            <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">Uptime</p>
            <p id="val-uptime" class="truncate font-mono text-base font-semibold text-slate-100">-</p>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl px-5 py-5">
            <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">OS Platform</p>
            <p id="val-os" class="truncate text-base font-semibold text-slate-100">-</p>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl px-5 py-5">
            <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">CPU Cores</p>
            <p id="val-cores" class="text-base font-semibold text-slate-100">-</p>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl px-5 py-5">
            <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">Processes</p>
            <p id="val-processes" class="text-base font-semibold text-slate-100">-</p>
        </div>

        <!-- =========================
             NETWORK
        ========================== -->
        <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-xl px-5 py-5">
            <div class="flex items-center justify-between">
                <div>
                    <p class="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                        <span class="text-emerald-400">↓</span> Download
                    </p>
                    <p id="val-net-down" class="font-mono text-2xl font-semibold tracking-tight text-emerald-400">
                        0 <span class="text-xs font-normal text-emerald-400/50">KB/s</span>
                    </p>
                </div>
                <div class="hidden h-8 w-8 items-center justify-center rounded-lg bg-emerald-400/[0.06] text-emerald-400/70 sm:flex">↓</div>
            </div>
        </div>

        <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-xl px-5 py-5">
            <div class="flex items-center justify-between">
                <div>
                    <p class="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                        <span class="text-pink-400">↑</span> Upload
                    </p>
                    <p id="val-net-up" class="font-mono text-2xl font-semibold tracking-tight text-pink-400">
                        0 <span class="text-xs font-normal text-pink-400/50">KB/s</span>
                    </p>
                </div>
                <div class="hidden h-8 w-8 items-center justify-center rounded-lg bg-pink-400/[0.06] text-pink-400/70 sm:flex">↑</div>
            </div>
        </div>

    </div>
</div>