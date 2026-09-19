async function uploadNewBackground(input) {
    if (!input.files || input.files.length === 0) return;
    const formData = new FormData();
    formData.append('file', input.files[0]);
    
    try {
        const res = await fetch('/settings/upload-bg', { method: 'POST', body: formData });
        const data = await res.json();
        
        if(data.status === 'success') {
            const select = document.getElementById('bg-media-select');
            if (select) {
                const option = document.createElement('option');
                option.value = data.file_url;
                option.text = input.files[0].name;
                select.appendChild(option);
                select.value = data.file_url;
            }
            
            Swal.fire({
                icon: 'success', 
                title: 'Uploaded!', 
                text: 'File berhasil ditambahkan ke list.', 
                background: '#1e293b', color: '#f8fafc', 
                timer: 1500, showConfirmButton: false
            });
        }
    } catch (e) {
        console.error("Upload error:", e);
        alert('Upload failed!');
    }
}

async function saveGlobalBg() {
    let type = 'color';
    const panelMedia = document.getElementById('panel-media');
    
    if (panelMedia && !panelMedia.classList.contains('hidden')) {
        if (document.getElementById('btn-type-image')?.classList.contains('bg-indigo-600')) type = 'image';
        if (document.getElementById('btn-type-video')?.classList.contains('bg-indigo-600')) type = 'video';
    }

    let val = '';
    const bright = document.getElementById('sliderBright')?.value || '1';

    if (type === 'color') {
        val = document.getElementById('bg-color-val')?.value || '#0f172a';
    } else {
        const urlInput = document.getElementById('bg-media-url')?.value || '';
        const selectInput = document.getElementById('bg-media-select')?.value || '';
        
        val = urlInput ? urlInput : selectInput;
        
        if (!val) {
            alert('Pilih gambar/video dari dropdown dulu, atau isi URL!');
            return;
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
        if (img) img.classList.add('hidden'); 
        if (vid) vid.classList.add('hidden');
    } else if (type === 'image') {
        if (globalBg) globalBg.style.backgroundColor = 'transparent';
        if (vid) vid.classList.add('hidden');
        if (img) {
            img.src = val; 
            img.classList.remove('hidden');
        }
    } else if (type === 'video') {
        if (globalBg) globalBg.style.backgroundColor = 'transparent';
        if (img) img.classList.add('hidden');
        if (vid) {
            vid.src = val; 
            vid.classList.remove('hidden');
        }
    }
    
    Swal.fire({
        icon: 'success', title: 'Saved!',
        text: 'Global background updated successfully.',
        background: '#1e293b', color: '#f8fafc',
        showConfirmButton: false, timer: 1500
    });
}