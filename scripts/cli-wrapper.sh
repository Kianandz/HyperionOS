#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Module: CLI Operator Tool Deployment
# -----------------------------------------------------------------------------

configure_cli_wrapper() {
    log_info "Compiling and persisting CLI tool..."

    sudo tee /usr/local/bin/hyperion > /dev/null << 'EOF'
#!/usr/bin/env bash
# ==============================================================================
# HyperionOS Operator CLI
# ==============================================================================

set -e

# --- Color Scheme ---
C_GREEN="\033[1;32m"
C_BLUE="\033[1;34m"
C_CYAN="\033[1;36m"
C_YELLOW="\033[1;33m"
C_RED="\033[1;31m"
C_RESET="\033[0m"
BOLD="\033[1m"

ACTION="${1:-help}"
APP_DIR="/HyperionOS"

print_header() {
    echo -e "${C_BLUE}${BOLD}====================================================${C_RESET}"
    echo -e "${C_CYAN}${BOLD}                 HyperionOS CLI                     ${C_RESET}"
    echo -e "${C_BLUE}${BOLD}====================================================${C_RESET}"
}

case "$ACTION" in
    start)
        echo -e "${C_CYAN}[i] Starting HyperionOS daemon...${C_RESET}"
        sudo systemctl start hyperion
        echo -e "${C_GREEN}[✔] Service is now running in the background.${C_RESET}"
        ;;
    stop)
        echo -e "${C_YELLOW}[i] Stopping HyperionOS daemon...${C_RESET}"
        sudo systemctl stop hyperion
        echo -e "${C_RED}[✔] Service has been stopped.${C_RESET}"
        ;;
    restart)
        echo -e "${C_CYAN}[i] Restarting HyperionOS daemon...${C_RESET}"
        sudo systemctl restart hyperion
        echo -e "${C_GREEN}[✔] Service successfully restarted.${C_RESET}"
        ;;
    dev|run)
        print_header
        echo -e "${C_YELLOW}[!] Starting in Developer Mode (Foreground / Root)${C_RESET}"
        echo -e "${C_CYAN}[i] Press Ctrl+C to exit and stop the process.${C_RESET}"
        echo -e "${C_BLUE}----------------------------------------------------${C_RESET}"
        # Execute directly as root for debugging
        sudo ${APP_DIR}/venv/bin/python ${APP_DIR}/main.py
        ;;
    status)
        print_header
        echo -e "${C_YELLOW}[ Daemon State ]${C_RESET}"
        sudo systemctl status hyperion --no-pager || true
        
        echo -e "\n${C_YELLOW}[ Network Telemetry ]${C_RESET}"
        MAIN_IFACE=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $5; exit}' || echo "Unknown")
        MAIN_IP=$(ip -4 addr show "$MAIN_IFACE" 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "Unknown")
        DNS_SERVERS=$(grep nameserver /etc/resolv.conf 2>/dev/null | awk '{print $2}' | paste -sd ", " || echo "Not Found")
        
        echo -e " ${C_GREEN}Primary IFace${C_RESET} : $MAIN_IFACE"
        echo -e " ${C_GREEN}IPv4 Address ${C_RESET} : $MAIN_IP"
        echo -e " ${C_GREEN}Resolvers    ${C_RESET} : $DNS_SERVERS"
        
        echo -e "\n${C_YELLOW}[ Socket Bindings ]${C_RESET}"
        sudo ss -tulpn | grep -E 'python|nginx|main\.py' || echo -e " ${C_RED}No tracked bindings active.${C_RESET}"
        echo -e "${C_BLUE}====================================================${C_RESET}"
        ;;
    set-user)
        NEW_USER="$2"
        NEW_PASS="$3"
        
        if [[ -z "$NEW_USER" || -z "$NEW_PASS" ]]; then
            echo -e "${C_RED}[✗] Syntax: hyperion set-user <new_username> <new_password>${C_RESET}"
            exit 1
        fi
        
        CURRENT_USER=$(stat -c '%U' /HyperionOS 2>/dev/null || echo "root")
        echo -e "${C_YELLOW}[i] Initiating migration sequence to '$NEW_USER'...${C_RESET}"
        
        if ! id "$NEW_USER" &>/dev/null; then
            sudo useradd -m -s /bin/bash "$NEW_USER"
        fi
        
        echo "$NEW_USER:$NEW_PASS" | sudo chpasswd
        echo -e "${C_GREEN}[✔] Authentication secrets rotated for '$NEW_USER'.${C_RESET}"
        
        if [[ "$CURRENT_USER" != "$NEW_USER" ]]; then
            echo -e "${C_YELLOW}[i] Realigning filesystem ownership & privileges...${C_RESET}"
            sudo usermod -aG docker "$NEW_USER"
            sudo usermod -aG adm "$NEW_USER"
            
            sudo chown -R "$NEW_USER:$NEW_USER" /var/www/html /etc/nginx /HyperionOS /var/log/nginx /etc/samba /var/www/nodes /etc/samba/shares.conf.d 2>/dev/null || true
            sudo chown -R "$NEW_USER:$NEW_USER" /etc/php 2>/dev/null || true
            sudo setfacl -m u:"$NEW_USER":rw /etc/resolv.conf 2>/dev/null || true
            
            echo -e "${C_GREEN}[✔] File ownership migration complete. Handled over to '$NEW_USER'.${C_RESET}"
        fi
        ;;
    log|logs)
        echo -e "${C_CYAN}[i] Streaming application logs (Press Ctrl+C to stop)...${C_RESET}"
        sudo journalctl -u hyperion -f
        ;;
    *)
        print_header
        echo -e "${C_CYAN}Available Commands:${C_RESET}"
        echo -e "  ${C_GREEN}hyperion start${C_RESET}                 - Bootstrap background service"
        echo -e "  ${C_GREEN}hyperion stop${C_RESET}                  - Terminate service layer"
        echo -e "  ${C_GREEN}hyperion restart${C_RESET}               - Power cycle the service"
        echo -e "  ${C_GREEN}hyperion status${C_RESET}                - Display system telemetry and health"
        echo -e "  ${C_GREEN}hyperion dev${C_RESET}                   - Run main.py directly in foreground (root)"
        echo -e "  ${C_GREEN}hyperion set-user <usr> <pwd>${C_RESET}  - Rotate ownership and security contexts"
        echo -e "  ${C_GREEN}hyperion logs${C_RESET}                  - Stream live application trace logs"
        echo -e "${C_BLUE}====================================================${C_RESET}"
        exit 1
        ;;
esac
EOF
    sudo chmod +x /usr/local/bin/hyperion
    log_success "CLI operational shell written."
}