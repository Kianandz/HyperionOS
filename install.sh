#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# HyperionOS Main Provisioning Orchestrator
# Maintainer: Platform Engineering Team
# -----------------------------------------------------------------------------

set -euo pipefail

# Ambil lokasi absolut direktori script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="${SCRIPT_DIR}/scripts"

# Load seluruh modul terpisah
source "${MODULES_DIR}/utils.sh"
source "${MODULES_DIR}/dependencies.sh"
source "${MODULES_DIR}/application.sh"
source "${MODULES_DIR}/security.sh"
source "${MODULES_DIR}/systemd.sh"
source "${MODULES_DIR}/cli-wrapper.sh"

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
    configure_nginx
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