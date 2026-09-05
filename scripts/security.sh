#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Module: Filesystem ACLs & Sudoers Security Configuration
# -----------------------------------------------------------------------------

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