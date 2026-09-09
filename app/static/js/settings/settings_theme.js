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