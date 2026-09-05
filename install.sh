#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# HyperionOS Bootstrap Script
# Maintainer: Platform Engineering Team
# -----------------------------------------------------------------------------
# Automates the initial provisioning, dependencies, user management, and service
# configuration for HyperionOS.
# -----------------------------------------------------------------------------

set -euo pipefail

# Color definitions for standard output
readonly C_GREEN='\033[0;32m'
readonly C_CYAN='\033[0;36m'
readonly C_YELLOW='\033[1;33m'
readonly C_RED='\033[0;31m'
readonly C_RESET='\033[0m'

readonly APP_DIR="/HyperionOS"
readonly APP_USER="hyperion"

log_info() { echo -e "${C_CYAN}[INFO]${C_RESET} $1"; }
log_success() { echo -e "${C_GREEN}[SUCCESS]${C_RESET} $1"; }
log_warn() { echo -e "${C_YELLOW}[WARN]${C_RESET} $1"; }
log_err() { echo -e "${C_RED}[ERROR]${C_RESET} $1" >&2; exit 1; }

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
    
    # Enforce non-interactive frontend to prevent hanging on interactive prompts (e.g., mariadb/mysql root password)
    export DEBIAN_FRONTEND=noninteractive

    # Updated: Switched mysql-server to mariadb-server for consistency, enforced modern Docker packages.
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
    
    # Copying files instead of git clone
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

    # Guarantee ownership is applied early so venv initialization won't fail due to root ownership
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

    # Execute securely scoped as the service account to prevent root-owned venv files
    sudo -u "${APP_USER}" $python_bin -m venv venv || log_err "Failed to establish virtual environment."
    
    sudo -u "${APP_USER}" "${APP_DIR}/venv/bin/pip" install --upgrade pip >/dev/null
    if [[ -f "${APP_DIR}/requirements.txt" ]]; then
        sudo -u "${APP_USER}" "${APP_DIR}/venv/bin/pip" install -r requirements.txt >/dev/null || log_warn "Non-critical failure while resolving pip requirements."
    fi
    
    log_success "Virtual environment synchronized."
}

configure_permissions() {
    log_info "Applying strict filesystem ACLs and ownership..."
    
    sudo mkdir -p /var/www/html /etc/nginx /etc/php /var/log/nginx
    sudo chown -R "${APP_USER}:${APP_USER}" /var/www/html /etc/nginx /var/log/nginx
    sudo chown -R "${APP_USER}:${APP_USER}" /etc/php 2>/dev/null || true

    sudo setfacl -m u:"${APP_USER}":rw /etc/resolv.conf 2>/dev/null || true

    log_info "Injecting dynamically scoped sudoers constraints..."
    sudo tee /etc/sudoers.d/hyperion > /dev/null <<EOF
${APP_USER} ALL=(ALL) NOPASSWD: /usr/sbin/nginx -t, /usr/bin/nginx -t
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl * nginx
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl * php-fpm, /usr/bin/systemctl * php8.3-fpm, /usr/bin/systemctl * php8.2-fpm, /usr/bin/systemctl * php8.1-fpm
${APP_USER} ALL=(ALL) NOPASSWD: /usr/sbin/ufw, /usr/bin/ufw
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/tail -n * /var/log/ufw.log
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/cloudflared
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl * cloudflared
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/journalctl -u cloudflared -n 50 --no-pager
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/apt-get update, /usr/bin/apt-get install -y mariadb-server, /usr/bin/apt-get install -y mysql-server
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/pacman -Sy --noconfirm mariadb
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/mariadb-install-db *
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl * mariadb, /usr/bin/systemctl * mysql
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/resolv.conf
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl * hyperion
${APP_USER} ALL=(ALL) NOPASSWD: /usr/bin/journalctl -u hyperion *
EOF
    sudo chmod 0440 /etc/sudoers.d/hyperion
    log_success "Filesystem and execution policies activated."
}

configure_systemd() {
    log_info "Generating Systemd unit specifications..."
    
    sudo tee /etc/systemd/system/hyperion.service > /dev/null <<EOF
[Unit]
Description=HyperionOS Daemon Service
After=network.target

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python main.py
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

configure_cli_wrapper() {
    log_info "Compiling and persisting CLI tool..."

    sudo tee /usr/local/bin/hyperion > /dev/null << 'EOF'
#!/usr/bin/env bash
# HyperionOS Operator CLI

set -e

ACTION="${1:-help}"

case "$ACTION" in
    start)
        sudo systemctl start hyperion
        echo -e "\033[0;32m[+] HyperionOS Service Started.\033[0m"
        ;;
    stop)
        sudo systemctl stop hyperion
        echo -e "\033[0;31m[-] HyperionOS Service Stopped.\033[0m"
        ;;
    restart)
        sudo systemctl restart hyperion
        echo -e "\033[1;33m[*] HyperionOS Service Restarted.\033[0m"
        ;;
    status)
        echo -e "\n\033[1;36m=== [ Daemon State ] ===\033[0m"
        sudo systemctl status hyperion --no-pager || true
        
        echo -e "\n\033[1;36m=== [ Network Telemetry ] ===\033[0m"
        MAIN_IFACE=$(ip route get 1.1.1.1 2>/dev/null | grep -Po '(?<=dev )(\S+)' || echo "Unknown")
        MAIN_IP=$(ip -4 addr show "$MAIN_IFACE" 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "Unknown")
        DNS_SERVERS=$(grep nameserver /etc/resolv.conf 2>/dev/null | awk '{print $2}' | paste -sd ", " || echo "Not Found")
        
        echo -e " \033[1;32mPrimary IFace\033[0m : $MAIN_IFACE"
        echo -e " \033[1;32mIPv4 Address \033[0m : $MAIN_IP"
        echo -e " \033[1;32mResolvers    \033[0m : $DNS_SERVERS"
        
        echo -e "\n\033[1;36m=== [ Socket Bindings ] ===\033[0m"
        sudo ss -tulpn | grep -E 'python|nginx|main\.py' || echo " No tracked bindings."
        echo ""
        ;;
    set-user)
        NEW_USER="$2"
        NEW_PASS="$3"
        
        if [[ -z "$NEW_USER" || -z "$NEW_PASS" ]]; then
            echo -e "\033[0;31m[!] Syntax: hyperion set-user <new_username> <new_password>\033[0m"
            exit 1
        fi
        
        CURRENT_USER=$(stat -c '%U' /HyperionOS)
        echo -e "\033[1;33m[*] Initiating migration sequence to '$NEW_USER'...\033[0m"
        
        if ! id "$NEW_USER" &>/dev/null; then
            sudo useradd -m -s /bin/bash "$NEW_USER"
        fi
        
        echo "$NEW_USER:$NEW_PASS" | sudo chpasswd
        echo -e "\033[0;32m[+] Authentication secrets rotated for '$NEW_USER'.\033[0m"
        
        if [[ "$CURRENT_USER" != "$NEW_USER" ]]; then
            echo -e "\033[1;33m[*] Realigning filesystem ownership & privileges...\033[0m"
            sudo usermod -aG docker "$NEW_USER"
            sudo usermod -aG adm "$NEW_USER"
            
            sudo chown -R "$NEW_USER:$NEW_USER" /var/www/html /etc/nginx /HyperionOS /var/log/nginx
            sudo chown -R "$NEW_USER:$NEW_USER" /etc/php 2>/dev/null || true
            sudo setfacl -m u:"$NEW_USER":rw /etc/resolv.conf 2>/dev/null || true
            
            echo -e "\033[1;33m[*] Patching privilege escalation boundaries...\033[0m"
            # Hardened regex patch: securely handles variable whitespace
            sudo sed -i -E "s/^${CURRENT_USER}([[:space:]]+)/${NEW_USER}\1/g" /etc/sudoers.d/hyperion
            
            echo -e "\033[1;33m[*] Updating daemon execution context...\033[0m"
            sudo sed -i "s/User=$CURRENT_USER/User=$NEW_USER/g" /etc/systemd/system/hyperion.service
            sudo sed -i "s/Group=$CURRENT_USER/Group=$NEW_USER/g" /etc/systemd/system/hyperion.service
            
            sudo systemctl daemon-reload
            sudo systemctl restart hyperion
            echo -e "\033[0;32m[+] Service migration complete. Handled over to '$NEW_USER'.\033[0m"
        fi
        ;;
    log|logs)
        sudo journalctl -u hyperion -f
        ;;
    *)
        echo -e "\033[1;36mHyperionOS CLI Specification:\033[0m"
        echo -e "  \033[0;32mhyperion start\033[0m                 - Bootstrap background service"
        echo -e "  \033[0;32mhyperion stop\033[0m                  - Terminate service layer"
        echo -e "  \033[0;32mhyperion restart\033[0m               - Power cycle the service"
        echo -e "  \033[0;32mhyperion status\033[0m                - Display system telemetry and logs"
        echo -e "  \033[0;32mhyperion set-user <usr> <pwd>\033[0m  - Rotate ownership and security contexts"
        echo -e "  \033[0;32mhyperion log\033[0m                   - Stream application trace logs"
        exit 1
        ;;
esac
EOF
    sudo chmod +x /usr/local/bin/hyperion
    log_success "CLI operational shell written."
}

# -----------------------------------------------------------------------------
# Main Orchestrator
# -----------------------------------------------------------------------------
main() {
    clear
    echo -e "${C_CYAN}"
    cat << "EOF"
 _   _                       _             ___  ____  
| | | |_   _ _ __   ___ _ __(_) ___  _ __ / _ \/ ___| 
| |_| | | | | '_ \ / _ \ '__| |/ _ \| '_ \ | | \___ \ 
|  _  | |_| | |_) |  __/ |  | | (_) | | | | |_| |___) |
|_| |_|\__, | .__/ \___|_|  |_|\___/|_| |_|\___/|____/ 
       |___/|_|                                        
EOF
    echo -e "${C_RESET}"
    echo "======================================================"
    echo -e "${C_GREEN}       HyperionOS Automated Provisioning Tool${C_RESET}"
    echo "======================================================"
    echo ""

    detect_os
    install_dependencies
    
    provision_user
    setup_application
    configure_venv
    
    configure_permissions
    configure_systemd
    configure_cli_wrapper

    echo -e "${C_CYAN}======================================================${C_RESET}"
    echo -e "${C_GREEN}      Provisioning Sequence Complete. System Online.${C_RESET}"
    echo -e "${C_GREEN}      Recommended next actions:${C_RESET}"
    echo -e "${C_YELLOW}      - hyperion start${C_RESET}"
    echo -e "${C_YELLOW}      - hyperion status${C_RESET}"
    echo -e "${C_CYAN}======================================================${C_RESET}"
}

main "$@"