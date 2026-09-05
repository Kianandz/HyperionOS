async function showLogs(service) {
        document.getElementById('logTitle').innerText = service;
        document.getElementById('logContent').innerText = '';
        document.getElementById('logLoading').classList.remove('hidden');
        openModal('modalLogs');

        try {
            const response = await fetch(`/websites/logs/${service}`);
            document.getElementById('logContent').innerText = response.ok ? await response.text() : 'Gagal mengambil log dari server.';
        } catch (error) {
            document.getElementById('logContent').innerText = 'Error fetch log: ' + error;
        } finally {
            document.getElementById('logLoading').classList.add('hidden');
        }
    }