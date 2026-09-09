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