async function createNewDB() {
    const { value: dbName } = await Swal.fire({ 
        title: "Buat Database Baru", input: 'text', placeholder: 'nama_db', 
        showCancelButton: true, background: '#0f172a', color: '#fff', confirmButtonText: 'Buat' 
    });
    if (!dbName) return; 

    const form = new FormData(); 
    form.append('db_name', dbName); 
    ['db_type', 'host', 'port', 'user', 'password'].forEach(k => form.append(k, document.getElementById('q_'+k).value)); 

    const res = await fetch('/databases/create-db', { method: 'POST', body: form }); 
    const data = await res.json(); 
    if (data.status === 'success') {
        Swal.fire({icon: 'success', title: 'Berhasil', background: '#0f172a', color: '#fff', timer: 1500}); 
        loadSelectedSession(document.getElementById("saved-sessions-list").value || "");  
    } else {
        Swal.fire({icon: 'error', title: 'Gagal', text: data.message, background: '#0f172a', color: '#fff'}); 
    }
}

function createNewTable() {
    const db = document.getElementById('q_database').value; 
    if (!db) return Swal.fire({icon: 'warning', title: 'Oops', text: 'Pilih database dulu dari panel kiri!', background: '#0f172a', color: '#fff'}); 
    
    document.getElementById('new_tbl_name').value = ''; 
    document.getElementById('new_tbl_columns').innerHTML = ''; 
    addColumnRow(true); 
    document.getElementById('modalCreateTable').classList.remove('hidden'); 
}

function addColumnRow(isFirst = false) {
    const tbody = document.getElementById('new_tbl_columns'); 
    const rowId = Date.now(); 
    const tr = document.createElement('tr'); 
    tr.id = `colrow_${rowId}`; 
    tr.className = "border-b border-slate-700/50 hover:bg-slate-900/50 transition-colors"; 
    
    tr.innerHTML = `
        <td class="p-2"><input type="text" class="col-name w-full bg-slate-950/80 border border-slate-700/50 rounded-lg px-3 py-2 outline-none text-xs font-mono focus:border-indigo-500" value="${isFirst ? 'id' : ''}" placeholder="nama_field"></td>
        <td class="p-2">
            <select class="col-type w-full bg-slate-950/80 border border-slate-700/50 rounded-lg px-3 py-2 outline-none text-xs font-mono focus:border-indigo-500">
                <option value="INT">INT</option>
                <option value="VARCHAR">VARCHAR</option>
                <option value="TEXT">TEXT</option>
                <option value="DATE">DATE</option>
                <option value="DATETIME">DATETIME</option>
                <option value="BOOLEAN">BOOLEAN</option>
            </select>
        </td>
        <td class="p-2"><input type="text" class="col-len w-full bg-slate-950/80 border border-slate-700/50 rounded-lg px-3 py-2 outline-none text-xs font-mono focus:border-indigo-500" value="${isFirst ? '11' : ''}" placeholder="255"></td>
        <td class="p-2 text-center"><input type="checkbox" class="col-ai rounded bg-slate-800 border-slate-600 text-indigo-500 focus:ring-indigo-500" ${isFirst ? 'checked' : ''}></td>
        <td class="p-2 text-center"><input type="radio" name="col_pk" class="col-pk bg-slate-800 border-slate-600 text-indigo-500" ${isFirst ? 'checked' : ''}></td>
        <td class="p-2 text-center"><button type="button" onclick="document.getElementById('colrow_${rowId}').remove()" class="text-rose-400 hover:text-rose-300 transition-colors"><i class="fa fa-trash"></i></button></td>
    `; 
    tbody.appendChild(tr); 
}

async function submitCreateTable() {
    const tblName = document.getElementById('new_tbl_name').value; 
    if(!tblName) return alert('Nama tabel harus diisi!'); 
    
    const rows = document.querySelectorAll('#new_tbl_columns tr'); 
    if(rows.length === 0) return alert('Minimal harus ada 1 field kolom!'); 
    
    let columns = []; 
    rows.forEach(tr => { 
        columns.push({
            name: tr.querySelector('.col-name').value, 
            type: tr.querySelector('.col-type').value, 
            length: tr.querySelector('.col-len').value, 
            ai: tr.querySelector('.col-ai').checked, 
            pk: tr.querySelector('.col-pk').checked 
        });
    });

    const form = new FormData(); 
    form.append('table_name', tblName); 
    form.append('columns', JSON.stringify(columns)); 
    ['db_type', 'host', 'port', 'user', 'password', 'database'].forEach(k => form.append(k, document.getElementById('q_'+k).value)); 

    const res = await fetch('/databases/create-table', { method: 'POST', body: form }); 
    const data = await res.json(); 
    
    if (data.status === 'success') {
        Swal.fire({icon: 'success', title: 'Tabel Terbuat', background: '#0f172a', color: '#fff', timer: 1500}); 
        document.getElementById('modalCreateTable').classList.add('hidden'); 
        htmx.trigger(document.querySelector('select[name="database"]'), 'change');  
    } else {
        Swal.fire({icon: 'error', title: 'Query Gagal', text: data.message, background: '#0f172a', color: '#fff'}); 
    }
}

function openAddColumnModal(tableName) {
    document.getElementById('add_col_table').value = tableName; 
    document.getElementById('add_col_name').value = ''; 
    document.getElementById('add_col_len').value = ''; 
    document.getElementById('add_col_ai').checked = false; 
    document.getElementById('modalAddColumn').classList.remove('hidden'); 
}

async function submitAddColumn() {
    const table = document.getElementById('add_col_table').value; 
    const name = document.getElementById('add_col_name').value; 
    
    if (!name) return alert('Nama field harus diisi!'); 

    const colData = {
        name: name, 
        type: document.getElementById('add_col_type').value, 
        length: document.getElementById('add_col_len').value, 
        ai: document.getElementById('add_col_ai').checked 
    };

    const form = new FormData(); 
    form.append('table', table); 
    form.append('column_data', JSON.stringify(colData)); 
    
    ['db_type', 'host', 'port', 'user', 'password', 'database'].forEach(k => form.append(k, document.getElementById('q_'+k).value)); 

    const res = await fetch('/databases/add-column', { method: 'POST', body: form }); 
    const data = await res.json(); 
    
    if (data.status === 'success') {
        Swal.fire({icon: 'success', title: 'Field Berhasil Ditambah', background: '#0f172a', color: '#fff', timer: 1500}); 
        document.getElementById('modalAddColumn').classList.add('hidden'); 
        
        const refreshForm = new FormData(); 
        refreshForm.append('table', table); 
        ['db_type', 'host', 'port', 'user', 'password', 'database'].forEach(k => refreshForm.append(k, document.getElementById('q_'+k).value)); 
        
        fetch('/databases/structure', { method: 'POST', body: refreshForm }) 
        .then(r => r.text()) 
        .then(html => {
            document.getElementById('data-view').innerHTML = html; 
        });
    } else {
        Swal.fire({icon: 'error', title: 'Gagal', text: data.message, background: '#0f172a', color: '#fff'}); 
    }
}

async function deleteTable(tableName) {
    const { isConfirmed } = await Swal.fire({ 
        title: `Hapus Tabel \`${tableName}\`?`, 
        text: "Semua data di dalam tabel ini bakal hilang permanen dan nggak bisa dibalikin!", 
        icon: 'warning', 
        showCancelButton: true, 
        confirmButtonColor: '#ef4444', 
        cancelButtonColor: '#334155', 
        background: '#0f172a', 
        color: '#fff', 
        confirmButtonText: 'Ya, Hapus!' 
    });

    if (isConfirmed) { 
        const form = new FormData(); 
        form.append('table', tableName); 
        
        ['db_type', 'host', 'port', 'user', 'password', 'database'].forEach(k => { 
            form.append(k, document.getElementById('q_'+k).value); 
        });

        const res = await fetch('/databases/drop-table', { method: 'POST', body: form }); 
        const data = await res.json(); 

        if (data.status === 'success') {
            Swal.fire({icon: 'success', title: 'Tabel Dihapus', background: '#0f172a', color: '#fff', timer: 1500}); 
            
            htmx.trigger(document.querySelector('select[name="database"]'), 'change'); 
            
            document.getElementById('data-view').innerHTML = `
                <div class="flex flex-col items-center justify-center h-64 text-slate-500 text-xs text-center space-y-2">
                    <i class="fa fa-table text-4xl mb-3 opacity-30"></i>
                    <p>Pilih database dan tabel di sidebar kiri untuk menampilkan isi data.</p>
                </div>
            `; 
        } else {
            Swal.fire({icon: 'error', title: 'Gagal Menghapus', text: data.message, background: '#0f172a', color: '#fff'}); 
        }
    }
}