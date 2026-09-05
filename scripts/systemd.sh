#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Module: Systemd Service Registration
# -----------------------------------------------------------------------------

configure_systemd() {
    log_info "Generating Systemd unit specifications..."
    
    sudo tee /etc/systemd/system/hyperion.service > /dev/null <<EOF
[Unit]
Description=HyperionOS Daemon Service
After=network.target

[Service]
User=root
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python /HyperionOS/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable hyperion >/dev/null 2>&1
    log_success "Systemd integration configured."
}