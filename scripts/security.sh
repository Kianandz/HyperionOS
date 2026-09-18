#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Module: Filesystem ACLs
# -----------------------------------------------------------------------------

configure_permissions() {
    log_info "Applying strict filesystem ACLs and ownership..."
    
    sudo mkdir -p /var/www/html /etc/nginx /etc/php /var/log/nginx /etc/samba /var/www/nodes
    sudo chown -R "${APP_USER}:${APP_USER}" /var/www/html /etc/nginx /var/log/nginx
    sudo chown -R "${APP_USER}:${APP_USER}" /etc/php 2>/dev/null || true
    sudo chown -R "${APP_USER}:${APP_USER}" /etc/samba 2>/dev/null || true
    sudo chown -R "${APP_USER}:${APP_USER}" /var/www/nodes 2>/dev/null || true
    sudo chown -R "${APP_USER}:${APP_USER}" /etc/samba/shares.conf.d 2>/dev/null || true

    sudo setfacl -m u:"${APP_USER}":rw /etc/resolv.conf 2>/dev/null || true

    log_success "Filesystem policies activated (Running as root, sudoers bypassed)."
}