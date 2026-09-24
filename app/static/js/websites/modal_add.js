// modal_add.js
function switchTab(mode) {
    document.getElementById('formMode').value = mode;
    if(mode === 'simple') {
        document.getElementById('tabSimple').className = "px-4 py-2 text-sm font-semibold text-indigo-400 border-b-2 border-indigo-500";
        document.getElementById('tabAdvanced').className = "px-4 py-2 text-sm font-semibold text-slate-400 hover:text-slate-300";
        document.getElementById('contentSimple').classList.remove('hidden');
        document.getElementById('contentAdvanced').classList.add('hidden');
    } else {
        document.getElementById('tabAdvanced').className = "px-4 py-2 text-sm font-semibold text-indigo-400 border-b-2 border-indigo-500";
        document.getElementById('tabSimple').className = "px-4 py-2 text-sm font-semibold text-slate-400 hover:text-slate-300";
        document.getElementById('contentAdvanced').classList.remove('hidden');
        document.getElementById('contentSimple').classList.add('hidden');
    }
}

function updateRootDir(domainValue) {
    const originalDomain = domainValue.trim();
    const safeDomain = originalDomain.split(/\s+/)[0]; 

    if (safeDomain) {
        document.getElementById('inputRootDir').value = '/var/www/html/' + safeDomain;
    } else {
        document.getElementById('inputRootDir').value = '/var/www/html/';
    }
    
    let rawArea = document.getElementById('rawConfigArea');
    let currentText = rawArea.value;
    
    currentText = currentText.replace(/server_name [^;]+;/, 'server_name ' + (originalDomain || 'example.com') + ';');
    currentText = currentText.replace(/root \/var\/www\/html\/[^;]+;/, 'root /var/www/html/' + (safeDomain || 'example.com') + ';');
    
    rawArea.value = currentText;
}