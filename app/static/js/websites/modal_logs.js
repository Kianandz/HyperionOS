// modal_logs_3.js
async function showLogs(service) {
    document.getElementById('logTitle').innerText = service;
    document.getElementById('logContent').innerText = '';
    document.getElementById('logLoading').classList.remove('hidden');
    openModal('modalLogs');

    try {
        const response = await fetch(`/websites/logs/${service}`);
        document.getElementById('logContent').innerText = response.ok ? await response.text() : 'Failed to fetch logs from server.';
    } catch (error) {
        document.getElementById('logContent').innerText = 'Error fetching log: ' + error;
    } finally {
        document.getElementById('logLoading').classList.add('hidden');
    }
}