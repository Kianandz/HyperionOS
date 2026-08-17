#!/usr/bin/env bash

# ==============================================================================
#  HyperionOS - Core Dashboard Uninstaller
# ==============================================================================

set -euo pipefail

# ANSI Color Codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

# Root privilege check
if [[ "$EUID" -ne 0 ]]; then
    log_error "This script must be run as root. Try 'sudo ./uninstall.sh'."
fi

echo -e "${RED}"
echo "======================================================"
echo "          HyperionOS Uninstallation Script            "
echo "======================================================"
echo -e "${NC}"

read -p "Are you sure you want to completely remove HyperionOS? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Uninstallation aborted."
    exit 0
fi

# ------------------------------------------------------------------------------
# 1. Stop & Disable Systemd Service
# ------------------------------------------------------------------------------
log_info "Stopping and disabling HyperionOS core service..."
if systemctl is-active --quiet hyperion.service 2>/dev/null; then
    systemctl stop hyperion.service
fi

if systemctl is-enabled --quiet hyperion.service 2>/dev/null; then
    systemctl disable hyperion.service
fi

# Remove service unit file
SERVICE_FILE="/etc/systemd/system/hyperion.service"
if [[ -f "$SERVICE_FILE" ]]; then
    log_info "Removing systemd service unit..."
    rm -f "$SERVICE_FILE"
    systemctl daemon-reload
fi

# ------------------------------------------------------------------------------
# 2. Web Server Configuration Cleanup
# ------------------------------------------------------------------------------
NGINX_CONF="/etc/nginx/conf.d/hyperion.conf"
if [[ -f "$NGINX_CONF" ]]; then
    log_info "Removing Nginx configuration..."
    rm -f "$NGINX_CONF"
    systemctl reload nginx 2>/dev/null || true
fi

# ------------------------------------------------------------------------------
# 3. Security & Privilege Cleanup
# ------------------------------------------------------------------------------
SUDOERS_FILE="/etc/sudoers.d/hyperion_kianandz"
if [[ -f "$SUDOERS_FILE" ]]; then
    log_info "Removing custom sudoers privileges..."
    rm -f "$SUDOERS_FILE"
fi

# ------------------------------------------------------------------------------
# 4. Binary CLI Tool Removal
# ------------------------------------------------------------------------------
CLI_FILE="/usr/local/bin/hyperion"
if [[ -f "$CLI_FILE" ]]; then
    log_info "Removing Hyperion CLI binary..."
    rm -f "$CLI_FILE"
fi

# ------------------------------------------------------------------------------
# 5. Directory Structure Cleanup
# ------------------------------------------------------------------------------
TARGET_DIR="/HyperionOS"
if [[ -d "$TARGET_DIR" ]]; then
    log_info "Removing application deployment directory ($TARGET_DIR)..."
    rm -rf "$TARGET_DIR"
fi

# ------------------------------------------------------------------------------
# 6. System User & Group Cleanup
# ------------------------------------------------------------------------------
if id "hyperion" &>/dev/null; then
    log_info "Removing system user 'hyperion'..."
    userdel hyperion 2>/dev/null || true
fi

if getent group "hyperion" &>/dev/null; then
    groupdel hyperion 2>/dev/null || true
fi

# ------------------------------------------------------------------------------
# Uninstallation Complete Summary
# ------------------------------------------------------------------------------
echo -e "\n${GREEN}======================================================${NC}"
echo -e " ${GREEN}HyperionOS has been successfully uninstalled!${NC}"
echo -e " Core dependencies (Nginx, Docker, MariaDB, PHP) were"
echo -e " preserved to avoid disrupting other running services."
echo -e "${GREEN}======================================================${NC}\n"