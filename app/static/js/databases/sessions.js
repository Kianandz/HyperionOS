const DB_SESSIONS_KEY = "HYPERION_DB_SESSIONS"; //

function getSavedSessions() {
    return JSON.parse(localStorage.getItem(DB_SESSIONS_KEY) || "[]"); 
}

function renderSessionDropdown() {
    const sessions = getSavedSessions(); 
    const select = document.getElementById("saved-sessions-list"); 
    select.innerHTML = '<option value="">-- Pilih Sesi Tersimpan --</option>'; 
    sessions.forEach((s, idx) => {
        select.innerHTML += `<option value="${idx}">${s.name} (${s.user}@${s.host}:${s.port})</option>`; 
    });
}

function loadSelectedSession(index) {
    if (index === "") return; 
    const session = getSavedSessions()[index]; 
    if (!session) return; 

    document.getElementById("q_db_type").value = session.db_type; 
    document.getElementById("q_host").value = session.host; 
    document.getElementById("q_port").value = session.port; 
    document.getElementById("q_user").value = session.user; 
    document.getElementById("q_password").value = session.password; 

    htmx.ajax('POST', '/databases/list-dbs', { 
        target: '#tables-explorer-container', 
        values: session 
    });
}

function openNewConnectionModal() {
    document.getElementById('new-connection-modal').classList.remove('hidden'); 
}

function closeNewConnectionModal() {
    document.getElementById('new-connection-modal').classList.add('hidden'); 
}

function handleSaveNewConnection(event) {
    event.preventDefault(); 
    
    const session = {
        name: document.getElementById('conn_name').value, 
        db_type: document.getElementById('conn_db_type').value, 
        host: document.getElementById('conn_host').value, 
        port: document.getElementById('conn_port').value, 
        user: document.getElementById('conn_user').value, 
        password: document.getElementById('conn_password').value 
    };

    const sessions = getSavedSessions(); 
    sessions.push(session); 
    localStorage.setItem(DB_SESSIONS_KEY, JSON.stringify(sessions)); 
    
    renderSessionDropdown(); 
    closeNewConnectionModal(); 
    
    const newIdx = sessions.length - 1; 
    document.getElementById("saved-sessions-list").value = newIdx; 
    loadSelectedSession(newIdx); 

    event.target.reset(); 
}

function useLocalSession() {
    const localSession = {
        db_type: "mysql", 
        host: "127.0.0.1", 
        port: 3306, 
        user: "root", 
        password: "" 
    };

    document.getElementById("q_db_type").value = localSession.db_type; 
    document.getElementById("q_host").value = localSession.host; 
    document.getElementById("q_port").value = localSession.port; 
    document.getElementById("q_user").value = localSession.user; 
    document.getElementById("q_password").value = localSession.password; 

    htmx.ajax('POST', '/databases/list-dbs', { 
        target: '#tables-explorer-container', 
        values: localSession 
    });
}

document.addEventListener("DOMContentLoaded", renderSessionDropdown); 