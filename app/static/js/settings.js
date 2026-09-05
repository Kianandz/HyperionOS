// Mengganti Tipe Background (Color / Image / Video)
function setBgType(type) {
    // Reset warna tombol
    document.getElementById('btn-type-color').className = "flex-1 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs font-bold transition";
    document.getElementById('btn-type-image').className = "flex-1 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs font-bold transition";
    document.getElementById('btn-type-video').className = "flex-1 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs font-bold transition";

    // Set tombol aktif
    document.getElementById(`btn-type-${type}`).className = "flex-1 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold transition";

    // Tampilkan panel yang sesuai
    if (type === 'color') {
        document.getElementById('panel-color').classList.remove('hidden');
        document.getElementById('panel-media').classList.add('hidden');
    } else {
        document.getElementById('panel-color').classList.add('hidden');
        document.getElementById('panel-media').classList.remove('hidden');
    }
}

// Toggle URL vs Upload Lokal
function toggleMediaInput() {
    const method = document.getElementById('mediaMethod').value;
    if (method === 'url') {
        document.getElementById('input-url').classList.remove('hidden');
        document.getElementById('input-upload').classList.add('hidden');
    } else {
        document.getElementById('input-url').classList.add('hidden');
        document.getElementById('input-upload').classList.remove('hidden');
    }
}

// Live Preview Slider Text & Value
function previewTheme() {
    const blurVal = document.getElementById('sliderBlur').value;
    const opacityVal = document.getElementById('sliderOpacity').value;
    
    // Update teks angka di UI
    document.getElementById('valBlur').innerText = blurVal + 'px';
    document.getElementById('valOpacity').innerText = opacityVal;

    // (Opsional) Terapkan langsung ke elemen background lu di sini
    // document.body.style.backdropFilter = `blur(${blurVal}px)`;
}

// Fungsi Simpan
function saveAdvancedTheme() {
    console.log("Menyimpan tema advanced...");
    // Tambahkan logika fetch API atau form submit ke backend lu di sini
    alert("Tema berhasil disimpan!");
}

function saveCardTheme() {
    // Ambil nilai dari UI
    const cardHex = document.getElementById('ui-card-color').value;
    const textHex = document.getElementById('ui-text-color').value;
    const cardOp = document.getElementById('ui-card-opacity').value;
    const cardBlur = document.getElementById('ui-card-blur').value;

    // Simpan ke localStorage
    const config = { cardHex, cardOp, cardBlur, textHex };
    localStorage.setItem('HYPERION_UI', JSON.stringify(config));

    // Convert ke RGBA biar tembus pandang
    const hexToRgba = (hex, alpha) => {
        let r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };

    // Langsung tembak ke CSS Root biar berubah tanpa reload!
    document.documentElement.style.setProperty('--theme-card-bg', hexToRgba(cardHex, cardOp));
    document.documentElement.style.setProperty('--theme-card-blur', cardBlur + 'px');
    document.documentElement.style.setProperty('--theme-text-main', textHex);

    // Alert SweetAlert2 yang bakal langsung nyesuaiin warna baru lu wkwk
    Swal.fire({
        icon: 'success',
        title: 'Styling Diperbarui!',
        text: 'Warna, opacity, dan blur berhasil diterapkan ke semua.',
        background: 'var(--theme-card-bg)', 
        color: 'var(--theme-text-main)',
        showConfirmButton: false, 
        timer: 1500
    });
}

async function saveGlobalBg() {
    let type = 'color';
    if (!document.getElementById('panel-media').classList.contains('hidden')) {
        // Ngecek mana yang aktif berdasarkan class tombol setBgType
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
            // Logic kalau upload file. Lu butuh nge-POST file ini ke FastAPI lu (misal via files.py)
            // trus balikin path /static/uploads/... nya.
            const fileInput = document.getElementById('bg-media-file');
            if (fileInput.files.length > 0) {
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                try {
                    // Sesuaikan endpoint upload di backend lu, misal /upload-bg
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
    
    // Terapin langsung tanpa reload kalau mau transisi mulus
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
    
    // Lu udah pake sweetalert2 di base.html
    Swal.fire({
        icon: 'success',
        title: 'Tersimpan!',
        text: 'Background global berhasil diupdate.',
        background: '#1e293b', color: '#f8fafc',
        showConfirmButton: false, timer: 1500
    });
}