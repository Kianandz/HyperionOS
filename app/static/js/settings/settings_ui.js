// settings_ui.js
// Change Background Type (Color / Image / Video)
function setBgType(type) {
    // Reset button colors
    document.getElementById('btn-type-color').className = "flex-1 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs font-bold transition";
    document.getElementById('btn-type-image').className = "flex-1 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs font-bold transition";
    document.getElementById('btn-type-video').className = "flex-1 py-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs font-bold transition";

    // Set active button
    document.getElementById(`btn-type-${type}`).className = "flex-1 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold transition";

    // Display corresponding panel
    if (type === 'color') {
        document.getElementById('panel-color').classList.remove('hidden');
        document.getElementById('panel-media').classList.add('hidden');
    } else {
        document.getElementById('panel-color').classList.add('hidden');
        document.getElementById('panel-media').classList.remove('hidden');
    }
}

// Toggle URL vs Local Upload
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
    
    // Update number text in UI
    document.getElementById('valBlur').innerText = blurVal + 'px';
    document.getElementById('valOpacity').innerText = opacityVal;

    // (Optional) Apply directly to your background element here
    // document.body.style.backdropFilter = `blur(${blurVal}px)`;
}

function toggleLogoInput() {
    const type = document.getElementById('logo-type').value;
    const uploadDiv = document.getElementById('logo-image-input');
    if (type === 'image') {
        uploadDiv.classList.remove('hidden');
    } else {
        uploadDiv.classList.add('hidden');
    }
}

async function saveBranding() {
    const name = document.getElementById('brand-name').value || 'HyperionOS';
    const type = document.getElementById('logo-type').value;
    const fileInput = document.getElementById('logo-upload');

    let brandCfg = { name: name, type: type, url: '' };

    // 1. Update APP_NAME ke backend (.env)
    const nameForm = new FormData();
    nameForm.append('name', name);
    try {
        await fetch('/settings/branding/name', {
            method: 'POST',
            body: nameForm
        });
    } catch (err) {
        console.error("Failed to update .env", err);
    }

    // 2. Kalau mode gambar dan ada file yang di-upload
    if (type === 'image' && fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/settings/upload-logo', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.status === 'success') {
                brandCfg.url = result.file_url;
            }
        } catch (err) {
            Swal.fire('Error', 'Failed to upload logo image', 'error');
            return;
        }
    } 
    // 3. Kalau mode gambar tapi nggak upload file baru (pake yang lama)
    else if (type === 'image') {
        const existing = JSON.parse(localStorage.getItem('HYPERION_BRAND'));
        if (existing && existing.url) brandCfg.url = existing.url;
    }

    // Simpan ke local storage buat load UI yang instan tanpa delay
    localStorage.setItem('HYPERION_BRAND', JSON.stringify(brandCfg));
    
    Swal.fire({
        title: 'Success!',
        text: 'Branding and .env applied successfully',
        icon: 'success',
        timer: 1500,
        showConfirmButton: false
    }).then(() => {
        window.location.reload();
    });
}