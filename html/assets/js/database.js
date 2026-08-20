function updateDefaultPort() {
    const type = document.getElementById('db-type').value;
    const portInput = document.getElementById('db-port');
    if (type === 'mysql') portInput.value = 3306;
    if (type === 'postgres') portInput.value = 5432;
    if (type === 'mssql') portInput.value = 1433;
}

function getPayload(includeDb = false) {
    const dbType = document.getElementById('db-type').value;
    const rawPort = parseInt(document.getElementById('db-port').value);
    const defaultPorts = { mysql: 3306, postgres: 5432, mssql: 1433 };

    const payload = {
        db_type: dbType,
        host: document.getElementById('db-host').value,
        port: !isNaN(rawPort) ? rawPort : defaultPorts[dbType],
        user: document.getElementById('db-user').value,
        password: document.getElementById('db-pass').value
    };

    if (includeDb) {
        payload.database = document.getElementById('selected-db').value;
        payload.query = document.getElementById('sql-query').value;
    }

    return payload;
}

async function selectDatabase(dbName) {
    const selectedInput = document.getElementById('selected-db');
    if (selectedInput) {
        selectedInput.value = dbName;
        selectedInput.classList.add('ring-2', 'ring-indigo-500');
        setTimeout(() => selectedInput.classList.remove('ring-2', 'ring-indigo-500'), 1000);
        
        // Update label UI
        document.getElementById('active-db-label').innerText = dbName;
        document.getElementById('table-explorer-section').classList.remove('hidden');
        
        // Langsung load tabel otomatis!
        await loadTablesGUI();
    }
}

async function connectDatabase() {
    const payload = getPayload();
    const statusMsg = document.getElementById('db-status-msg');
    const dbList = document.getElementById('db-list');

    statusMsg.className = "text-sm text-yellow-400 animate-pulse";
    statusMsg.innerText = "Connecting to database server...";
    dbList.classList.add('hidden');

    try {
        const res = await fetch(`${API_BASE}/databases/test-connection`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok) {
            statusMsg.className = "text-sm text-emerald-400 font-semibold";
            statusMsg.innerText = data.message;

            dbList.innerHTML = '';
            data.databases.forEach(db => {
                dbList.innerHTML += `
                    <li onclick="selectDatabase('${db}')" class="bg-slate-950 p-3 rounded border border-slate-800 flex items-center justify-between text-indigo-300 cursor-pointer hover:border-indigo-500 transition">
                        <span class="cursor-pointer"><i class="fa fa-solid fa-database mr-2 text-slate-500"></i> ${db}</span>
                        <span class="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400">Select</span>
                    </li>
                `;
            });
            dbList.classList.remove('hidden');
        } else {
            statusMsg.className = "text-sm text-rose-400 font-semibold";
            statusMsg.innerText = `Error: ${data.detail}`;
        }
    } catch (err) {
        statusMsg.className = "text-sm text-rose-400 font-semibold";
        statusMsg.innerText = "Failed to connect backend FastAPI!";
    }
}

async function runSqlQuery() {
    const dbName = document.getElementById('selected-db').value;
    const query = document.getElementById('sql-query').value;
    const statusMsg = document.getElementById('query-status');
    const tableContainer = document.getElementById('query-result-container');
    const tableHead = document.getElementById('query-table-head');
    const tableBody = document.getElementById('query-table-body');

    if (!dbName || !query) {
        alert("Select database first & then exec query!");
        return;
    }

    statusMsg.innerText = "Running query...";
    statusMsg.className = "text-xs text-yellow-400 font-mono animate-pulse";

    const payload = getPayload(true);

    try {
        const res = await fetch(`${API_BASE}/databases/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok) {
            statusMsg.className = "text-xs text-emerald-400 font-mono";
            
            if (data.type === 'select') {
                statusMsg.innerText = `Fetched ${data.row_count} rows.`;

                tableHead.innerHTML = `<tr>${data.columns.map(col => `<th class="p-3">${col}</th>`).join('')}</tr>`;

                tableBody.innerHTML = data.data.map(row => {
                    return `<tr class="hover:bg-slate-800/50">${
                        data.columns.map(col => {
                            let cellValue = row[col];
                            if (cellValue === null || cellValue === undefined) {
                                return `<td class="p-3 whitespace-nowrap"><span class="text-slate-600 italic">NULL</span></td>`;
                            }
                            if (typeof cellValue === 'object') {
                                cellValue = JSON.stringify(cellValue);
                            }
                            return `<td class="p-3 whitespace-nowrap max-w-xs truncate" title="${cellValue}">${cellValue}</td>`;
                        }).join('')
                    }</tr>`;
                }).join('');

                tableContainer.classList.remove('hidden');
            } else {
                statusMsg.innerText = data.message;
                tableContainer.classList.add('hidden');
            }
        } else {
            statusMsg.className = "text-xs text-rose-400 font-mono";
            statusMsg.innerText = `Error: ${data.detail}`;
            tableContainer.classList.add('hidden');
        }
    } catch (err) {
        statusMsg.className = "text-xs text-rose-400 font-mono";
        statusMsg.innerText = "Failed to execute query!";
    }
}

async function loadTablesGUI() {
    const dbType = document.getElementById('db-type').value;
    const tableListContainer = document.getElementById('table-list-gui');
    tableListContainer.innerHTML = '<span class="text-sm text-yellow-400 animate-pulse">Fetching tables...</span>';

    // Sesuaikan query berdasarkan engine database
    let query = "";
    if (dbType === 'mysql') query = "SHOW TABLES;";
    if (dbType === 'postgres') query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';";
    if (dbType === 'mssql') query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';";

    // Pura-pura ngisi query ke textarea console biar getPayload() bisa dipake ulang
    document.getElementById('sql-query').value = query; 
    
    const payload = getPayload(true);

    try {
        const res = await fetch(`${API_BASE}/databases/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.type === 'select') {
            tableListContainer.innerHTML = '';

            data.data.forEach(row => {
                const tableName = Object.values(row)[0]; 
                tableListContainer.innerHTML += `
                    <button onclick="loadTableData('${tableName}')" class="bg-slate-800 hover:bg-indigo-600 text-indigo-300 hover:text-white px-3 py-1 rounded border border-slate-700 text-sm transition flex items-center">
                        <i class="fa fa-table mr-2"></i> ${tableName}
                    </button>
                `;
            });
        }
    } catch (err) {
        tableListContainer.innerHTML = '<span class="text-sm text-rose-400">Gagal load tabel!</span>';
    }
}

async function loadTableData(tableName) {
    // Generate query SELECT * otomatis
    const autoQuery = `SELECT * FROM ${tableName} LIMIT 100;`;
    
    // Set text area (biar user tetep bisa edit/custom query-nya di console)
    document.getElementById('sql-query').value = autoQuery;
    
    // Panggil fungsi runSqlQuery() lu yang udah mantap itu buat ngerender table HTML
    await runSqlQuery();
}