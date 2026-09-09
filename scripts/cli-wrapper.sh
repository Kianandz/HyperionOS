#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Module: CLI Operator Tool Deployment
# -----------------------------------------------------------------------------

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
            
            sudo chown -R "$NEW_USER:$NEW_USER" /var/www/html /etc/nginx /HyperionOS /var/log/nginx /etc/samba
            sudo chown -R "$NEW_USER:$NEW_USER" /etc/php 2>/dev/null || true
            sudo setfacl -m u:"$NEW_USER":rw /etc/resolv.conf 2>/dev/null || true
            
            echo -e "\033[1;33m[*] Patching privilege escalation boundaries...\033[0m"
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