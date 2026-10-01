// modal_edit.js
let syntaxCheckTimer;
const rawConfigArea = document.getElementById('editRawConfigArea');
const syntaxStatus = document.getElementById('syntaxStatus');

rawConfigArea.addEventListener('input', () => {
    clearTimeout(syntaxCheckTimer);
    
    syntaxStatus.innerHTML = '<i class="fa fa-circle-notch fa-spin text-amber-400"></i> <span class="text-amber-400">Checking syntax...</span>';
    rawConfigArea.classList.remove('border-emerald-500', 'border-rose-500');
    rawConfigArea.classList.add('border-purple-500'); 

    syntaxCheckTimer = setTimeout(async () => {
        const configContent = rawConfigArea.value;
        
        if (!configContent.trim()) {
            syntaxStatus.innerHTML = '';
            return;
        }

        const formData = new FormData();
        formData.append('raw_config', configContent);
        
        try {
            const res = await fetch('/websites/test-syntax', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                syntaxStatus.innerHTML = '<i class="fa fa-check-circle text-emerald-400"></i> <span class="text-emerald-400">Syntax OK</span>';

                rawConfigArea.classList.replace('border-purple-500', 'border-emerald-500');
            } else {
                const errorMsg = data.message.replace(/"/g, '&quot;');
                syntaxStatus.innerHTML = `<i class="fa fa-times-circle text-rose-400"></i> <span class="text-rose-400 cursor-help" title="${errorMsg}">Syntax Bad!</span>`;

                rawConfigArea.classList.replace('border-purple-500', 'border-rose-500');
            }
        } catch (e) {
            syntaxStatus.innerHTML = '<i class="fa fa-exclamation-triangle text-rose-500"></i> <span class="text-rose-500">Check Failed</span>';
        }
    }, 1000); 
});

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
        document.getElementById('editRawConfigArea').value = data.config || ('# Error: ' + (data.message || 'Data Empty'));
    } catch (e) {
        document.getElementById('editRawConfigArea').value = '# Connection Error';
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