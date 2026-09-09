async function saveGlobalBg() {
    let type = 'color';
    if (!document.getElementById('panel-media').classList.contains('hidden')) {
        if (document.getElementById('btn-type-image').classList.contains('bg-indigo-600')) type = 'image';
        if (document.getElementById('btn-type-video').classList.contains('bg-indigo-600')) type = 'video';
    }

    let val = '';
    const bright = document.getElementById('sliderBright').value;
    const method = document.getElementById('mediaMethod').value;

    if (type === 'color') {
        val = document.getElementById('bg-color-val').value;
    } else {
        if (method === 'url') {
            val = document.getElementById('bg-media-url').value;
        } else {
            const fileInput = document.getElementById('bg-media-file');
            if (fileInput.files.length > 0) {
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                try {
                    const res = await fetch('/settings/upload-bg', { method: 'POST', body: formData });
                    const data = await res.json();
                    val = data.file_url;
                } catch (e) {
                    alert('Upload gagal, pastiin endpoint backend siap.');
                    return;
                }
            } else {
                alert('Pilih file dulu!'); return;
            }
        }
    }

    const config = { type, val, bright };
    localStorage.setItem('HYPERION_BG', JSON.stringify(config));
    
    document.documentElement.style.setProperty('--bg-bright', bright);
    const globalBg = document.getElementById('global-bg');
    const img = document.getElementById('bg-img');
    const vid = document.getElementById('bg-video');

    if (type === 'color') {
        document.documentElement.style.setProperty('--bg-color', val);
        img.classList.add('hidden');
        vid.classList.add('hidden');
    } else if (type === 'image') {
        globalBg.style.backgroundColor = 'transparent';
        vid.classList.add('hidden');
        img.src = val;
        img.classList.remove('hidden');
    } else if (type === 'video') {
        globalBg.style.backgroundColor = 'transparent';
        img.classList.add('hidden');
        vid.src = val;
        vid.classList.remove('hidden');
    }
    
    Swal.fire({
        icon: 'success',
        title: 'Tersimpan!',
        text: 'Background global berhasil diupdate.',
        background: '#1e293b', color: '#f8fafc',
        showConfirmButton: false, timer: 1500
    });
}