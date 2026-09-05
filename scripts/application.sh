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

    sudo -u "${APP_USER}" tee "${APP_DIR}/.env" > /dev/null <<EOF
APP_NAME=HyperionOS
VERSION=1.0.0
SECRET_KEY=${secret_key}
EOF
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