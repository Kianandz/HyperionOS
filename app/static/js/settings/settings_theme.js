// settings_theme.js
// Save Function
function saveAdvancedTheme() {
    console.log("Saving advanced theme...");
    // Add fetch API logic or form submission to your backend here
    alert("Theme saved successfully!");
}

function saveCardTheme() {
    // Get values from UI
    const cardHex = document.getElementById('ui-card-color').value;
    const textHex = document.getElementById('ui-text-color').value;
    const cardOp = document.getElementById('ui-card-opacity').value;
    const cardBlur = document.getElementById('ui-card-blur').value;

    // Save to localStorage
    const config = { cardHex, cardOp, cardBlur, textHex };
    localStorage.setItem('HYPERION_UI', JSON.stringify(config));

    // Convert to RGBA for transparency
    const hexToRgba = (hex, alpha) => {
        let r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };

    // Apply directly to CSS Root to update without page reload!
    document.documentElement.style.setProperty('--theme-card-bg', hexToRgba(cardHex, cardOp));
    document.documentElement.style.setProperty('--theme-card-blur', cardBlur + 'px');
    document.documentElement.style.setProperty('--theme-text-main', textHex);

    // SweetAlert2 alert that automatically matches your new colors
    Swal.fire({
        icon: 'success',
        title: 'Styling Updated!',
        text: 'Color, opacity, and blur successfully applied to all.',
        background: 'var(--theme-card-bg)', 
        color: 'var(--theme-text-main)',
        showConfirmButton: false, 
        timer: 1500
    });
}