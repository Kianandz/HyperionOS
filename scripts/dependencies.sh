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
    log_info "Bootstrapping system dependencies with fallback resolution..."
    
    export DEBIAN_FRONTEND=noninteractive

    if [[ "$PKG_MANAGER" == "apt" ]]; then
        sudo apt-get update -yqq || log_warn "APT update returned non-zero, proceeding..."
        
        sudo dpkg --configure -a >/dev/null 2>&1 || true
        sudo apt-get install -f -yqq >/dev/null 2>&1 || true

        local -r CORE_DEPS="curl git openssl python3 python3-venv python3-pip nginx mariadb-server ufw libpam0g-dev acl iproute2"
        
        log_info "Resolving core utilities and network packages..."
        sudo apt-get install -y $CORE_DEPS || log_err "Critical failure: Unable to resolve core dependencies."

        log_info "Resolving PHP-FPM environment..."
        sudo apt-get install -y php-fpm || \
        sudo apt-get install -y php8.2-fpm || \
        sudo apt-get install -y php8.3-fpm || \
        log_err "Critical failure: PHP-FPM and fallbacks could not be installed."

        log_info "Resolving Docker engine..."
        sudo apt-get install -y docker.io || \
        sudo apt-get install -y docker-ce || \
        log_err "Critical failure: Docker engine could not be installed."

        log_info "Resolving Docker Compose..."
        sudo apt-get install -y docker-compose-plugin || \
        sudo apt-get install -y docker-compose || \
        log_err "Critical failure: Docker Compose could not be installed."

    elif [[ "$PKG_MANAGER" == "pacman" ]]; then
        sudo pacman -Syu --noconfirm
        
        local -r ARCH_CORE="curl git openssl python python-pip nginx mariadb ufw acl iproute2"
        
        log_info "Resolving core utilities..."
        sudo pacman -S --noconfirm --needed $ARCH_CORE || log_err "Critical failure: Arch core dependencies failed."

        log_info "Resolving PHP-FPM environment..."
        sudo pacman -S --noconfirm --needed php-fpm || log_err "Critical failure: PHP-FPM could not be installed."

        log_info "Resolving Docker ecosystem..."
        sudo pacman -S --noconfirm --needed docker docker-compose || log_err "Critical failure: Docker packages failed."
    fi

    install_cloudflared
    log_success "System dependencies satisfied."
}