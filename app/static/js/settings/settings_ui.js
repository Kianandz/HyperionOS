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