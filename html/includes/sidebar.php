<aside class="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between">
    <div>
        <div class="p-6 border-b border-slate-800 flex items-center space-x-3">
            <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center font-bold text-xl">H</div>
            <span class="text-xl font-bold tracking-wider text-white">Hyperion<span class="text-indigo-500">OS</span></span>
        </div>
        <nav class="p-4 space-y-1">
    <a href="#home" onclick="switchTab('home')" class="flex items-center space-x-3 px-4 py-3 text-slate-300 hover:bg-slate-800 hover:text-white rounded-lg transition active-link" id="nav-dashboard">
        <i class="fa fa-pie-chart w-5"></i><span>Home</span>
    </a>
    <a href="#websites" onclick="switchTab('websites')" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition" id="nav-websites">
        <i class="fa fa-globe w-5"></i><span>Kelola Website</span>
    </a>
    <a href="#database" onclick="switchTab('database')" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition" id="nav-database">
        <i class="fa fa-database w-5"></i><span>Database</span>
    </a>
    <a href="#docker" onclick="switchTab('docker')" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition" id="nav-docker">
        <i class="fa fa-cubes w-5"></i><span>Docker</span>
    </a>
    <a href="#firewall" onclick="switchTab('firewall')" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition" id="nav-firewall">
        <i class="fa fa-shield w-5"></i><span>Firewall (UFW)</span>
    </a>
    <a href="#files" onclick="switchTab('files')" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition" id="nav-files">
        <i class="fa fa-folder-open w-5"></i><span>File Manager</span>
    </a>
    <a href="#cloudflared" onclick="switchTab('cloudflared')" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition" id="nav-cloudflared">
        <i class="fa fa-cloud w-5"></i><span>Cloudflared</span>
    </a>
    <a href="#settings" onclick="switchTab('settings')" class="flex items-center space-x-3 px-4 py-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition" id="nav-settings">
        <i class="fa fa-cog w-5"></i><span>Settings</span>
    </a>
</nav>
    </div>

    <div class="p-4 border-t border-slate-800">
        <a href="#logout" class="flex items-center space-x-3 px-4 py-3 text-rose-400 hover:bg-rose-500/10 rounded-lg transition" id="logoutBtn">
            <i class="fa-solid fa-right-from-bracket w-5"></i><span>Logout</span>
        </a>
    </div>
</aside>