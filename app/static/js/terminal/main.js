// main_4.js
(function initTerminal() {
    const termContainer = document.getElementById('terminal-container');
    
    // Prevent terminal from loading twice due to HTMX
    if (!termContainer || termContainer.dataset.initialized === 'true') return;
    termContainer.dataset.initialized = 'true';

    // Initialize Xterm
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

    // Add a short delay to ensure the addon-image CDN script is fully loaded by HTMX
    setTimeout(() => {
        if (window.ImageAddon) {
            const imageAddon = new window.ImageAddon.ImageAddon();
            term.loadAddon(imageAddon);
        } else {
            console.warn("xterm-addon-image failed to load from CDN.");
        }
    }, 500);

    term.open(termContainer);
    
    // Wait until DOM rendering is fully complete before fitting the size
    setTimeout(() => fitAddon.fit(), 100);

    // Resize terminal when the window resizes
    window.addEventListener('resize', () => {
        if(document.getElementById('terminal-container')) {
            fitAddon.fit();
        }
    });

    // WebSocket connection to FastAPI Backend
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
        term.write('\r\n\x1b[31m[!] Terminal connection disconnected from server.\x1b[0m\r\n');
    };

    // IMPORTANT: Clean up WebSocket when switching menus to prevent memory leaks
    document.body.addEventListener('htmx:beforeSwap', function cleanup() {
        if (ws.readyState === WebSocket.OPEN) ws.close();
        document.body.removeEventListener('htmx:beforeSwap', cleanup);
    });
})();