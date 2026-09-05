#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Module: OS Detection & System Dependency Provisioning
# -----------------------------------------------------------------------------

detect_os() {
    log_info "Probing operating system family..."
    if [[ ! -f /etc/os-release ]]; then
        log_err "Missing /etc/os-release. Cannot determine OS."
    fi

    source /etc/os-release
    if [[ "$ID" == "debian" || "${ID_LIKE:-}" == *"debian"* ]]; then
        PKG_MANAGER="apt"
    elif [[ "$ID" == "arch" || "${ID_LIKE:-}" == *"arch"* ]]; then
        PKG_MANAGER="pacman"
    else
        log_err "Unsupported OS family. Debian or Arch Linux required."
    fi
    log_success "Detected $PKG_MANAGER-based distribution."
}

install_cloudflared() {
    if command -v cloudflared &> /dev/null; then
        log_info "Cloudflared daemon is already present."
        return 0
    fi

    log_info "Deploying Cloudflared daemon..."
    if [[ "$PKG_MANAGER" == "apt" ]]; then
        sudo mkdir -p --mode=0755 /usr/share/keyrings
        curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
        echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list >/dev/null
        sudo apt-get update -yqq
        sudo apt-get install -yqq cloudflared
    elif [[ "$PKG_MANAGER" == "pacman" ]]; then
        curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
        sudo chmod +x /tmp/cloudflared
        sudo mv /tmp/cloudflared /usr/local/bin/cloudflared
    fi
}

install_dependencies() {
    log_info "Bootstrapping system dependencies..."
    
    export DEBIAN_FRONTEND=noninteractive

    local -r DEBIAN_DEPS="curl git openssl python3 python3-venv python3-pip nginx php-fpm mariadb-server ufw docker.io docker-compose-plugin libpam0g-dev acl iproute2"
    local -r ARCH_DEPS="curl git openssl python python-pip nginx php-fpm mariadb ufw docker docker-compose acl iproute2"

    if [[ "$PKG_MANAGER" == "apt" ]]; then
        sudo apt-get update -yqq
        sudo apt-get install -yqq $DEBIAN_DEPS
    elif [[ "$PKG_MANAGER" == "pacman" ]]; then
        sudo pacman -Sy --noconfirm
        sudo pacman -S --noconfirm --needed $ARCH_DEPS
    fi

    install_cloudflared
    log_success "System dependencies satisfied."
}