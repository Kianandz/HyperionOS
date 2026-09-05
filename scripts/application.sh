#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Module: User Provisioning & Application Deployment
# -----------------------------------------------------------------------------

provision_user() {
    log_info "Provisioning service account '${APP_USER}'..."
    
    if id "${APP_USER}" &>/dev/null; then
        log_info "Service account '${APP_USER}' already exists."
    else
        sudo useradd -m -s /bin/bash "${APP_USER}"
        echo "${APP_USER}:${APP_USER}" | sudo chpasswd
        log_success "Service account '${APP_USER}' provisioned."
    fi

    sudo usermod -aG docker "${APP_USER}"
    sudo usermod -aG adm "${APP_USER}"
}

setup_application() {
    log_info "Deploying application payload from local directory..."
    
    if [[ "$PWD" != "${APP_DIR}" ]]; then
        if [[ -d "${APP_DIR}" ]]; then
            local backup_dir="${APP_DIR}_backup_$(date +%Y%m%d%H%M%S)"
            log_warn "Target directory ${APP_DIR} exists. Archiving to ${backup_dir}..."
            sudo mv "${APP_DIR}" "${backup_dir}"
        fi
        
        log_info "Copying repository files from $PWD to ${APP_DIR}..."
        sudo cp -r "$PWD" "${APP_DIR}" || log_err "Local copy failed. Ensure you are running this inside the HyperionOS directory."
    else
        log_info "Running directly from target directory ${APP_DIR}. Skipping file copy."
    fi

    sudo chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

    local secret_key
    secret_key=$(openssl rand -base64 64 | tr -d '\n')

    log_info "Allocating random available port for application..."
    local app_port
    while true; do
        # Generate port acak di rentang 8000 - 9999
        app_port=$((RANDOM % 2000 + 8000))
        
        # Cek apakah port sedang dipakai (menggunakan ss atau netstat)
        if ! sudo ss -tulpn | grep -q ":${app_port} "; then
            break
        fi
    done
    log_success "Assigned port: ${app_port}"

    sudo -u "${APP_USER}" tee "${APP_DIR}/.env" > /dev/null <<EOF
APP_NAME=HyperionOS
VERSION=1.0.0
PORT=${app_port}
SECRET_KEY=${secret_key}
EOF

    sudo ufw default allow incoming
    sudo ufw default allow outgoing
    
    log_success "Application payload deployed."
}

configure_venv() {
    log_info "Initializing Python virtual environment..."
    
    cd "${APP_DIR}" || log_err "Failed to access application directory."
    
    local python_bin="python3"
    if ! command -v python3 &> /dev/null; then
        python_bin="python"
    fi

    sudo -u "${APP_USER}" $python_bin -m venv venv || log_err "Failed to establish virtual environment."
    
    sudo -u "${APP_USER}" "${APP_DIR}/venv/bin/pip" install --upgrade pip >/dev/null
    if [[ -f "${APP_DIR}/requirements.txt" ]]; then
        sudo -u "${APP_USER}" "${APP_DIR}/venv/bin/pip" install -r requirements.txt >/dev/null || log_warn "Non-critical failure while resolving pip requirements."
    fi
    
    log_success "Virtual environment synchronized."
}

configure_nginx() {
    log_info "Updating Nginx core configuration..."
    
    # Backup existing configuration if it exists
    if [[ -f /etc/nginx/nginx.conf ]]; then
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
        log_info "Created backup of the existing nginx.conf"
    fi
    
    # Write new configuration
    sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
#user http;
worker_processes auto;

# Load all installed dynamic modules
include modules.d/*.conf;

events {
    worker_connections 1024;
    multi_accept on;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    # Core optimizations
    types_hash_max_size 2048;
    types_hash_bucket_size 64;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    # Load modular configuration files
    include conf.d/*.conf;
}
EOF

    # Validate the new configuration
    if sudo nginx -t > /dev/null 2>&1; then
        log_success "Nginx configuration updated and tested successfully."
    else
        log_error "Nginx configuration test failed. Please check the syntax."
        return 1
    fi
}