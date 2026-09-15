(function initTerminal() {
    const termContainer = document.getElementById('terminal-container');
    
    if (!termContainer || termContainer.dataset.initialized === 'true') return;
    termContainer.dataset.initialized = 'true';

    const term = new Terminal({
        cursorBlink: true,
        theme: {
            background: '#020617',
            foreground: '#f1f5f9',
            cursor: '#818cf8',
        },
        fontFamily: '"Fira Code", monospace',
        fontSize: 13
    });
    
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);

    setTimeout(() => {
        if (window.ImageAddon) {
            const imageAddon = new window.ImageAddon.ImageAddon();
            term.loadAddon(imageAddon);
        } else {
            console.warn("xterm-addon-image failed to load from CDN.");
        }
    }, 500);

    term.open(termContainer);
    
    setTimeout(() => {
        fitAddon.fit();
    }, 100);

    const resizeObserver = new ResizeObserver(() => {
        requestAnimationFrame(() => {
            if (termContainer.clientWidth > 0 && termContainer.clientHeight > 0) {
                try {
                    fitAddon.fit();
                } catch (e) {}
            }
        });
    });
    
    resizeObserver.observe(termContainer);

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

    document.body.addEventListener('htmx:beforeSwap', function cleanup() {
        if (ws.readyState === WebSocket.OPEN) ws.close();
        resizeObserver.disconnect();
        document.body.removeEventListener('htmx:beforeSwap', cleanup);
    });
})();