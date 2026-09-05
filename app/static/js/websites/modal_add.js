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
        const cleanDomain = domainValue.replace(/[^a-zA-Z0-9.-]/g, '');
        document.getElementById('inputRootDir').value = '/var/www/html/' + cleanDomain;
        let rawArea = document.getElementById('rawConfigArea');
        let currentText = rawArea.value;
        currentText = currentText.replace(/server_name [^;]+;/, 'server_name ' + (cleanDomain || 'example.com') + ';');
        currentText = currentText.replace(/root \/var\/www\/html\/[^;]+;/, 'root /var/www/html/' + (cleanDomain || 'example.com') + ';');
        rawArea.value = currentText;
    }