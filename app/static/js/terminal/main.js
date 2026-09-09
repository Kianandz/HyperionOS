(function initTerminal() {
    const termContainer = document.getElementById('terminal-container');
    
    // Cegah terminal di-load dua kali gara-gara HTMX
    if (!termContainer || termContainer.dataset.initialized === 'true') return;
    termContainer.dataset.initialized = 'true';

    // Inisialisasi Xterm
    const term = new Terminal({
        cursorBlink: true,
        theme: {
            background: '#020617', // slate-950
            foreground: '#f1f5f9', // slate-100
            cursor: '#818cf8',     // indigo-400
        },
        fontFamily: '"Fira Code", monospace',
        fontSize: 13
    });
    
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);

    // Kasih delay dikit biar script CDN addon-image keburu di-load sepenuhnya oleh HTMX
    setTimeout(() => {
        if (window.ImageAddon) {
            const imageAddon = new window.ImageAddon.ImageAddon();
            term.loadAddon(imageAddon);
        } else {
            console.warn("xterm-addon-image gagal di-load dari CDN.");
        }
    }, 500);

    term.open(termContainer);
    
    // Tunggu DOM bener-bener nge-render selesai baru di-fit ukurannya
    setTimeout(() => fitAddon.fit(), 100);

    // Resize terminal kalau window berubah
    window.addEventListener('resize', () => {
        if(document.getElementById('terminal-container')) {
            fitAddon.fit();
        }
    });

    // Koneksi WebSocket ke Backend FastAPI
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/terminal/ws`);

    ws.onopen = () => {
        term.focus();
    };

    ws.onmessage = (event) => {
        term.write(event.data);
    };

    term.onData((data) => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(data);
        }
    });

    ws.onclose = () => {
        term.write('\r\n\x1b[31m[!] Koneksi terminal terputus dari server.\x1b[0m\r\n');
    };

    // PENTING: Bersihkan WebSocket pas pindah menu biar gak memory leak
    document.body.addEventListener('htmx:beforeSwap', function cleanup() {
        if (ws.readyState === WebSocket.OPEN) ws.close();
        document.body.removeEventListener('htmx:beforeSwap', cleanup);
    });
})();