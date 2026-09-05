function updateBatchActionState() {
    const checkedCount = document.querySelectorAll('input[name="row_ids"]:checked').length; 
    document.getElementById('btn-batch-duplicate').disabled = checkedCount === 0; 
    document.getElementById('btn-batch-delete').disabled = checkedCount === 0; 
}

function triggerBatchAction(action) {
    const checked = document.querySelectorAll('input[name="row_ids"]:checked'); 
    if (checked.length === 0) return; 

    const mode = document.getElementById('query_result_mode')?.value || 'data'; 
    let tableName = document.getElementById('query_result_table')?.value; 

    if (!tableName) {
        const queryText = document.querySelector('textarea[name="query"]').value; 
        const match = queryText.match(/(?:FROM|INTO|UPDATE)\s+`?([^`\s]+)`?/i); 
        if (!match) {
            alert('Gagal nentuin nama tabel dari query. Pastiin query formatnya bener.'); 
            return; 
        }
        tableName = match[1]; 
    }

    const formData = new FormData(); 
    formData.append('action', action); 
    formData.append('table', tableName); 
    formData.append('primary_key', 'id'); 
    
    ['db_type', 'host', 'port', 'user', 'password', 'database'].forEach(k => { 
        formData.append(k, document.getElementById('q_' + k).value); 
    });
    
    checked.forEach(cb => formData.append('row_ids', cb.value)); 

    const endpoint = mode === 'structure' ? '/databases/batch-structure-action' : '/databases/batch-action'; 

    fetch(endpoint, { method: 'POST', body: formData }) 
    .then(res => res.text()) 
    .then(html => {
        document.getElementById('data-view').insertAdjacentHTML('afterbegin', html); 
        if (mode === 'structure') {
            fetch('/databases/structure', { method: 'POST', body: formData }) 
            .then(r => r.text()) 
            .then(structHtml => document.getElementById('data-view').innerHTML = structHtml); 
        } else {
            htmx.trigger('#inline-query-box form', 'submit'); 
        }
    });
}

function toggleSelectAllRows(source) {
    const checkboxes = document.querySelectorAll('input[name="row_ids"]'); 
    checkboxes.forEach(cb => cb.checked = source.checked); 
    updateBatchActionState(); 
}

document.addEventListener('change', function(e) {
    if (e.target && e.target.name === 'row_ids') { 
        updateBatchActionState(); 
    }
});

async function quickEditRow(btn) {
    const cols = JSON.parse(btn.getAttribute('data-cols')); 
    const rowData = JSON.parse(btn.getAttribute('data-row')); 
    
    const pkCol = cols[0];  
    const pkVal = rowData[0]; 
    
    let htmlForm = `<div class="space-y-4 text-left">`; 
    cols.forEach((col, idx) => { 
        const val = rowData[idx] === null ? '' : rowData[idx]; 
        const isReadonly = idx === 0 ? 'readonly disabled' : '';  
        htmlForm += `
            <div>
                <label class="block text-xs text-slate-400 font-medium mb-1.5">${col} ${idx === 0 ? '(PK)' : ''}</label>
                <input type="text" id="edit_${col}" value="${val}" ${isReadonly} class="w-full bg-slate-950/80 border border-slate-700/50 text-emerald-400 text-xs rounded-xl p-3 outline-none focus:border-indigo-500 font-mono transition-all">
            </div>`; 
    });
    htmlForm += `</div>`; 

    const { isConfirmed } = await Swal.fire({ 
        title: `Edit Row (${pkCol}: ${pkVal})`, 
        html: htmlForm, 
        background: '#0f172a', color: '#fff', showCancelButton: true, confirmButtonText: 'Save Changes' 
    });

    if (isConfirmed) { 
        const match = document.querySelector('textarea[name="query"]').value.match(/FROM\s+`?([^`\s]+)`?/i); 
        const table = match ? match[1] : ''; 

        const formData = new FormData(); 
        formData.append('table', table); 
        formData.append('primary_key', pkCol); 
        formData.append('pk_value', pkVal); 
        
        ['db_type', 'host', 'port', 'user', 'password', 'database'].forEach(k => formData.append(k, document.getElementById('q_'+k).value)); 
        
        cols.forEach((col, idx) => { 
            if(idx !== 0) formData.append(col, document.getElementById(`edit_${col}`).value); 
        });

        fetch('/databases/update-row', { method: 'POST', body: formData }) 
        .then(res => res.text()) 
        .then(msg => {
            document.getElementById('data-view').insertAdjacentHTML('afterbegin', msg); 
            htmx.trigger('#inline-query-box form', 'submit'); 
        });
    }
}

async function openAddRowModal(btnElement) {
    const cols = JSON.parse(btnElement.getAttribute('data-cols')); 
    let htmlForm = `<div class="space-y-4 text-left max-h-[60vh] overflow-y-auto px-2">`; 
    cols.forEach((col, idx) => { 
        const placeholder = idx === 0 ? 'Kosongkan jika Auto Increment' : ''; 
        htmlForm += `
            <div>
                <label class="block text-xs text-slate-400 font-medium mb-1.5">${col}</label>
                <input type="text" id="addrow_${col}" placeholder="${placeholder}" class="w-full bg-slate-950/80 border border-slate-700/50 text-emerald-400 text-xs rounded-xl p-3 outline-none focus:border-indigo-500 font-mono transition-all">
            </div>`; 
    });
    htmlForm += `</div>`; 

    const { isConfirmed } = await Swal.fire({ 
        title: 'Tambah Data Baru', 
        html: htmlForm, 
        background: '#0f172a', color: '#fff',  
        showCancelButton: true, confirmButtonText: 'Simpan Data' 
    });

    if (isConfirmed) { 
        const match = document.querySelector('textarea[name="query"]').value.match(/FROM\s+`?([^`\s]+)`?/i); 
        const table = match ? match[1] : ''; 
        if(!table) return Swal.fire('Error', 'Gagal deteksi nama tabel dari query!', 'error'); 

        const formData = new FormData(); 
        formData.append('table', table); 
        
        ['db_type', 'host', 'port', 'user', 'password', 'database'].forEach(k => formData.append(k, document.getElementById('q_'+k).value)); 
        
        cols.forEach(col => { 
            const val = document.getElementById(`addrow_${col}`).value; 
            if(val !== '') formData.append(col, val);  
        });

        fetch('/databases/insert-row', { method: 'POST', body: formData }) 
        .then(res => res.text()) 
        .then(msg => {
            document.getElementById('data-view').insertAdjacentHTML('afterbegin', msg); 
            htmx.trigger('#inline-query-box form', 'submit');  
        });
    }
}

function changePage(direction) {
    const textarea = document.querySelector('textarea[name="query"]'); 
    let query = textarea.value.trim(); 
    
    const limitMatch = query.match(/LIMIT\s+(\d+)/i); 
    const limit = limitMatch ? parseInt(limitMatch[1]) : 100; 
    
    let offset = 0; 
    const offsetMatch = query.match(/OFFSET\s+(\d+)/i); 
    if (offsetMatch) offset = parseInt(offsetMatch[1]); 
    
    offset += (direction * limit); 
    if (offset < 0) offset = 0;  
    
    if (limitMatch && offsetMatch) {
        query = query.replace(/OFFSET\s+\d+/i, `OFFSET ${offset}`); 
    } else if (limitMatch && !offsetMatch) {
        query = query.replace(/LIMIT\s+\d+/i, `LIMIT ${limit} OFFSET ${offset}`); 
    } else {
        query = query.replace(/;$/, '') + ` LIMIT ${limit} OFFSET ${offset};`; 
    }
    
    textarea.value = query; 
    htmx.trigger('#inline-query-box form', 'submit');  
}

function applyQuickSearch(keyword, columnsData) {
    const columns = typeof columnsData === 'string' ? JSON.parse(columnsData) : columnsData; 
    
    const textarea = document.querySelector('textarea[name="query"]'); 
    let query = textarea.value.trim(); 
    
    const match = query.match(/FROM\s+`?([^`\s]+)`?/i); 
    if (!match) return Swal.fire('Error', 'Gagal deteksi tabel dari query!', 'error'); 
    const table = match[1]; 
    
    if (!keyword) { 
        textarea.value = `SELECT * FROM \`${table}\` LIMIT 25;`; 
    } else {
        const conditions = columns.map(col => `\`${col}\` LIKE '%${keyword}%'`).join(' OR '); 
        textarea.value = `SELECT * FROM \`${table}\` WHERE ${conditions} LIMIT 25;`; 
    }
    
    htmx.trigger('#inline-query-box form', 'submit'); 
}