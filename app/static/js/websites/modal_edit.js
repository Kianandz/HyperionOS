async function openEditModal(domain) {
        document.getElementById('editDomainTitle').innerText = domain;
        document.getElementById('editInputDomain').value = domain;
        document.getElementById('editInputRootDir').value = `/var/www/html/${domain}`;
        
        switchEditTab('advanced');
        document.getElementById('editRawConfigArea').value = 'Loading config...';
        openModal('modalEditWebsite');

        try {
            const res = await fetch(`/websites/config/${domain}`);
            const data = await res.json();
            document.getElementById('editRawConfigArea').value = data.config || ('# Error: ' + (data.message || 'Data kosong'));
        } catch (e) {
            document.getElementById('editRawConfigArea').value = '# Error koneksi';
        }
    }

    function switchEditTab(mode) {
        document.getElementById('editFormMode').value = mode;
        if(mode === 'simple') {
            document.getElementById('editTabSimple').className = "px-4 py-2 text-sm font-semibold text-purple-400 border-b-2 border-purple-500";
            document.getElementById('editTabAdvanced').className = "px-4 py-2 text-sm font-semibold text-slate-400 hover:text-slate-300";
            document.getElementById('editContentSimple').classList.remove('hidden');
            document.getElementById('editContentAdvanced').classList.add('hidden');
        } else {
            document.getElementById('editTabAdvanced').className = "px-4 py-2 text-sm font-semibold text-purple-400 border-b-2 border-purple-500";
            document.getElementById('editTabSimple').className = "px-4 py-2 text-sm font-semibold text-slate-400 hover:text-slate-300";
            document.getElementById('editContentAdvanced').classList.remove('hidden');
            document.getElementById('editContentSimple').classList.add('hidden');
        }
    }