<div id="section-home" class="mx-auto max-w-7xl px-4 py-6 text-slate-200 sm:px-6 lg:px-8">

    <div class="grid grid-cols-1 gap-4 md:grid-cols-4">

        <!-- =========================
             HEADER
        ========================== -->
        <div class="md:col-span-1 rounded-2xl bg-slate-900/95 p-6 ring-1 ring-white/[0.04]">
            <div class="flex h-full flex-col justify-between">

                <div>
                    <div class="mb-3 flex items-center gap-2">
                        <span class="h-1.5 w-1.5 rounded-full bg-indigo-400"></span>

                        <span class="text-[10px] font-bold uppercase tracking-[0.18em] text-indigo-400">
                            Server Monitor
                        </span>
                    </div>

                    <h1 class="text-2xl font-semibold tracking-tight text-white">
                        System Overview
                    </h1>

                    <p id="val-hostname"
                       class="mt-1.5 flex items-center gap-1.5 font-mono text-[11px] text-slate-500">
                        <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round"
                                  stroke-linejoin="round"
                                  stroke-width="2"
                                  d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/>
                        </svg>
                        Host: Loading...
                    </p>
                </div>

                <!-- Status -->
                <div class="mt-5 flex items-center gap-2 rounded-full bg-emerald-400/[0.08] px-3 py-1.5">
                    <span class="relative flex h-2 w-2">
                        <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50"></span>
                        <span class="relative h-2 w-2 rounded-full bg-emerald-400"></span>
                    </span>

                    <span class="text-[10px] font-bold uppercase tracking-widest text-emerald-400">
                        Online
                    </span>
                </div>

            </div>
        </div>


        <!-- =========================
             CPU
        ========================== -->
        <div class="md:col-span-2 rounded-2xl bg-slate-900/95 p-6 ring-1 ring-white/[0.04]">

            <div class="flex h-full flex-col justify-center">

                <p class="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                    CPU Usage
                </p>

                <div class="flex items-end justify-between gap-4">
                    <p id="val-cpu"
                       class="font-mono text-4xl font-semibold tracking-tight text-white">
                        0%
                    </p>

                    <div class="mb-1 h-1.5 w-32 overflow-hidden rounded-full bg-slate-800">
                        <div id="bar-cpu"
                             class="h-full rounded-full bg-indigo-500 transition-[width] duration-700 ease-out"
                             style="width: 0%">
                        </div>
                    </div>
                </div>

            </div>
        </div>


        <!-- =========================
             MEMORY
        ========================== -->
        <div class="md:col-span-2 rounded-2xl bg-slate-900/95 p-6 ring-1 ring-white/[0.04]">

            <div class="flex h-full items-center justify-between gap-6">

                <div>
                    <p class="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                        Memory
                    </p>

                    <p id="val-ram"
                       class="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                        0 / 0 GB
                    </p>
                </div>

                <div class="shrink-0">
                    <div id="val-ram-percent"
                         class="rounded-lg bg-blue-500/[0.08] px-3 py-2 font-mono text-xs font-semibold text-blue-400 ring-1 ring-blue-400/10">
                        0% used
                    </div>
                </div>

            </div>

            <div class="mt-5 h-1.5 overflow-hidden rounded-full bg-slate-800">
                <div id="bar-ram"
                     class="h-full rounded-full bg-blue-500 transition-[width] duration-700 ease-out"
                     style="width: 0%">
                </div>
            </div>

        </div>


        <!-- =========================
             STORAGE
        ========================== -->
        <div class="md:col-span-2 rounded-2xl bg-slate-900/95 p-6 ring-1 ring-white/[0.04]">

            <div class="mb-4 flex items-center gap-2">
                <svg class="h-4 w-4 text-slate-500"
                     fill="none"
                     stroke="currentColor"
                     viewBox="0 0 24 24">
                    <path stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/>
                </svg>

                <span class="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                    Storage Volumes
                </span>
            </div>

            <div id="disk-list"
                 class="space-y-4">
            </div>

        </div>


        <!-- =========================
             SMALL STATS
        ========================== -->

        <div class="rounded-2xl bg-slate-900/95 px-5 py-5 ring-1 ring-white/[0.04]">
            <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                Uptime
            </p>

            <p id="val-uptime"
               class="truncate font-mono text-base font-semibold text-slate-100">
                -
            </p>
        </div>


        <div class="rounded-2xl bg-slate-900/95 px-5 py-5 ring-1 ring-white/[0.04]">
            <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                OS Platform
            </p>

            <p id="val-os"
               class="truncate text-base font-semibold text-slate-100">
                -
            </p>
        </div>


        <div class="rounded-2xl bg-slate-900/95 px-5 py-5 ring-1 ring-white/[0.04]">
            <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                CPU Cores
            </p>

            <p id="val-cores"
               class="text-base font-semibold text-slate-100">
                -
            </p>
        </div>


        <div class="rounded-2xl bg-slate-900/95 px-5 py-5 ring-1 ring-white/[0.04]">
            <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                Processes
            </p>

            <p id="val-processes"
               class="text-base font-semibold text-slate-100">
                -
            </p>
        </div>


        <!-- =========================
             NETWORK
        ========================== -->

        <div class="md:col-span-2 rounded-2xl bg-slate-900/95 px-5 py-5 ring-1 ring-white/[0.04]">
            <div class="flex items-center justify-between">

                <div>
                    <p class="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                        <span class="text-emerald-400">↓</span>
                        Download
                    </p>

                    <p id="val-net-down"
                       class="font-mono text-2xl font-semibold tracking-tight text-emerald-400">
                        0
                        <span class="text-xs font-normal text-emerald-400/50">
                            KB/s
                        </span>
                    </p>
                </div>

                <div class="hidden h-8 w-8 items-center justify-center rounded-lg bg-emerald-400/[0.06] text-emerald-400/70 sm:flex">
                    ↓
                </div>

            </div>
        </div>


        <div class="md:col-span-2 rounded-2xl bg-slate-900/95 px-5 py-5 ring-1 ring-white/[0.04]">
            <div class="flex items-center justify-between">

                <div>
                    <p class="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                        <span class="text-pink-400">↑</span>
                        Upload
                    </p>

                    <p id="val-net-up"
                       class="font-mono text-2xl font-semibold tracking-tight text-pink-400">
                        0
                        <span class="text-xs font-normal text-pink-400/50">
                            KB/s
                        </span>
                    </p>
                </div>

                <div class="hidden h-8 w-8 items-center justify-center rounded-lg bg-pink-400/[0.06] text-pink-400/70 sm:flex">
                    ↑
                </div>

            </div>
        </div>

    </div>
</div>