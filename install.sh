#!/usr/bin/env bash

# ==============================================================================
#  HyperionOS - Core Dashboard Installer
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
    log_error "This script must be run as root. Try 'sudo ./install.sh'."
fi

echo -e "${GREEN}"
echo "  _  _                  _                 ____   _____ "
echo " | || |               _(_)               / __ \ / ____|"
echo " | || |  _   _ _ __  ___ _ __  ___  _ __  | |  | | (___  "
echo " | __ | | | | | '_ \/ _ \ | '__/ _ \| '_ \ | |  | |\___ \ "
echo " | || | | |_| | |_) |  __/ | | | (_) | | | || |__| |____) |"
echo " |_||_|  \__, | .__/ \___|_|_|  \___/|_| |_| \____/|_____/ "
echo "          __/ | |                                          "
echo "         |___/|_|      Installer System Panel              "
echo -e "${NC}"

# ------------------------------------------------------------------------------
# 1. OS Detection
# ------------------------------------------------------------------------------
log_info "Detecting operating system..."

if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_NAME="${ID:-}"
    OS_LIKE="${ID_LIKE:-}"
else
    log_error "Unable to detect OS (missing /etc/os-release)."
fi

# ------------------------------------------------------------------------------
# 2. Pre-Check & Package Installation & Base Dependencies
# ------------------------------------------------------------------------------

log_info "Checking system dependencies..."

declare -A CMDS=(
    ["nginx"]="nginx"
    ["php"]="php"
    ["php-fpm"]="php-fpm"
    ["mariadb"]="mariadb"
    ["ufw"]="ufw"
    ["docker"]="docker"
    ["python3"]="python3"
    ["pip3"]="pip3"
    ["curl"]="curl"
    ["git"]="git"
    ["jq"]="jq"
    ["cloudflared"]="cloudflared"
)

MISSING_PKGS=()

for pkg in "${!CMDS[@]}"; do
    cmd="${CMDS[$pkg]}"
    if command -v "$cmd" &>/dev/null; then
        log_success "  [✓] $pkg is installed"
    else
        log_warn "  [✗] $pkg is missing"
        MISSING_PKGS+=("$pkg")
    fi
done

if [[ ${#MISSING_PKGS[@]} -eq 0 ]]; then
    log_info "All core dependencies are met. Skipping package installation."
else
    log_info "Missing dependencies to be installed: ${MISSING_PKGS[*]}"
fi

if [[ ${#MISSING_PKGS[@]} -gt 0 ]]; then
    log_info "Installing missing system dependencies..."

    if [[ "$OS_NAME" == "arch" || "$OS_LIKE" == *"arch"* ]]; then
        PKG_MANAGER="pacman"
        
        pacman -Sy --noconfirm
        pacman -S --needed --noconfirm \
            nginx php php-fpm mariadb ufw docker python python-pip \
            python-virtualenv curl sudo git jq

    elif [[ "$OS_NAME" =~ ^(debian|ubuntu)$ || "$OS_LIKE" =~ (debian|ubuntu) ]]; then
        PKG_MANAGER="apt"
        export DEBIAN_FRONTEND=noninteractive
        
        apt-get update -y
        apt-get install -y --no-install-recommends \
            nginx php-cli php-fpm php-mysql mariadb-server ufw docker.io \
            python3 python3-pip python3-venv curl sudo git jq

    else
        log_error "Unsupported OS distribution ($OS_NAME). Supported: Arch Linux, Debian, Ubuntu."
    fi
else
    if [[ "$OS_NAME" == "arch" || "$OS_LIKE" == *"arch"* ]]; then
        PKG_MANAGER="pacman"
    else
        PKG_MANAGER="apt"
    fi
fi

# ------------------------------------------------------------------------------
# Cloudflared Setup
# ------------------------------------------------------------------------------
if ! command -v cloudflared &>/dev/null; then
    log_info "Cloudflared not found. Installing binary..."
    if [[ "$PKG_MANAGER" == "pacman" ]]; then
        pacman -S --needed --noconfirm cloudflared || log_warn "Failed to install cloudflared via pacman. Install manually if required."
    else
        ARCH=$(uname -m)
        case "$ARCH" in
            x86_64) CF_ARCH="amd64" ;;
            aarch64|arm64) CF_ARCH="arm64" ;;
            *) CF_ARCH="amd64" ;;
        esac

        curl -fsSL -o /tmp/cloudflared.deb "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${CF_ARCH}.deb" && \
            dpkg -i /tmp/cloudflared.deb || apt-get install -f -y
        rm -f /tmp/cloudflared.deb
    fi
else
    log_success "  [✓] cloudflared is already installed"
fi

# ------------------------------------------------------------------------------
# Enable Core Services
# ------------------------------------------------------------------------------
log_info "Enabling core background services..."
systemctl enable --now docker mariadb ufw 2>/dev/null || systemctl enable --now docker mysql ufw

# ------------------------------------------------------------------------------
# 3. User & Permissions Setup
# ------------------------------------------------------------------------------
log_info "Configuring system user 'hyperion'..."
if ! id "hyperion" &>/dev/null; then
    useradd -r -s /usr/sbin/nologin hyperion
    log_success "Created system user 'hyperion'."
else
    log_info "User 'hyperion' already exists."
fi

log_info "Adding 'hyperion' to docker group..."
usermod -aG docker hyperion

log_info "Setting up sudoers privileges for 'kianandz'..."
SUDOERS_FILE="/etc/sudoers.d/hyperion_kianandz"
cat << 'EOF' > "$SUDOERS_FILE"
kianandz ALL=(ALL) NOPASSWD: /usr/sbin/nginx, /bin/systemctl reload nginx, /bin/systemctl start nginx, /bin/systemctl stop nginx, /bin/systemctl restart nginx
kianandz ALL=(ALL) NOPASSWD: /usr/bin/systemctl * php-fpm
kianandz ALL=(ALL) NOPASSWD: /usr/bin/systemctl * nginx
kianandz ALL=(ALL) NOPASSWD: /usr/bin/journalctl -u *
EOF
chmod 0440 "$SUDOERS_FILE"

# ------------------------------------------------------------------------------
# 4. Directory Structure & Source Deployment
# ------------------------------------------------------------------------------
TARGET_DIR="/HyperionOS"
log_info "Creating deployment directory structure at $TARGET_DIR..."

mkdir -p "$TARGET_DIR/app"
mkdir -p "$TARGET_DIR/html"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy source app & html langsung ke target
if [[ -d "$SCRIPT_DIR/app" && -d "$SCRIPT_DIR/html" ]]; then
    log_info "Deploying application source files to $TARGET_DIR..."
    cp -r "$SCRIPT_DIR/app/"* "$TARGET_DIR/app/" 2>/dev/null || true
    cp -r "$SCRIPT_DIR/html/"* "$TARGET_DIR/html/" 2>/dev/null || true
fi

# Copy requirements.txt ke root Target
if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
    cp "$SCRIPT_DIR/requirements.txt" "$TARGET_DIR/requirements.txt"
fi

# ------------------------------------------------------------------------------
# 5. Python Environment & Backend Dependencies
# ------------------------------------------------------------------------------
log_info "Setting up Python environment..."
if [[ ! -d "$TARGET_DIR/venv" ]]; then
    python3 -m venv "$TARGET_DIR/venv"
fi

if [[ -f "$TARGET_DIR/requirements.txt" ]]; then
    log_info "Installing Python dependencies..."
    "$TARGET_DIR/venv/bin/pip" install --quiet --upgrade pip
    "$TARGET_DIR/venv/bin/pip" install --quiet -r "$TARGET_DIR/requirements.txt"
fi

# Apply permissions khusus folder panel
log_info "Setting directory permissions..."
chown -R hyperion:hyperion "$TARGET_DIR"
chmod -R 755 "$TARGET_DIR"

# ------------------------------------------------------------------------------
# 6. Systemd Service Setup
# ------------------------------------------------------------------------------
log_info "Configuring systemd service for Hyperion Core Engine..."
SERVICE_FILE="/etc/systemd/system/hyperion.service"

cat << EOF > "$SERVICE_FILE"
[Unit]
Description=HyperionOS Core Backend Engine
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=hyperion
Group=hyperion
WorkingDirectory=$TARGET_DIR
ExecStart=$TARGET_DIR/venv/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now hyperion.service

# ------------------------------------------------------------------------------
# 7. Nginx Web Server Configuration
# ------------------------------------------------------------------------------
log_info "Configuring Nginx reverse proxy..."
NGINX_CONF="/etc/nginx/conf.d/hyperion.conf"

PHP_SOCK=$(find /run/php/ -name "*.sock" 2>/dev/null | head -n 1)
if [[ -z "$PHP_SOCK" ]]; then
    PHP_SOCK="127.0.0.1:9000"
else
    PHP_SOCK="unix:$PHP_SOCK"
fi

cat << EOF > "$NGINX_CONF"
server {
    listen 80;
    server_name _;
    root $TARGET_DIR/html;
    index index.php index.html;

    location / {
        try_files \$uri \$uri/ /index.php?\$args;
    }

    # Proxy API requests to FastAPI engine
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass $PHP_SOCK;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
    }
}
EOF

# Restart web stack
log_info "Reloading web server services..."
systemctl restart php-fpm 2>/dev/null || systemctl restart php*-fpm 2>/dev/null || true
systemctl restart nginx

# ------------------------------------------------------------------------------
# 8. Hyperion CLI Tool
# ------------------------------------------------------------------------------
log_info "Installing Hyperion management CLI tool..."
CLI_FILE="/usr/local/bin/hyperion"

cat << 'EOF' > "$CLI_FILE"
#!/usr/bin/env bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

case "$1" in
    start)
        echo -e "${BLUE}[HyperionOS]${NC} Starting services..."
        sudo systemctl start hyperion.service nginx
        echo -e "${GREEN}[HyperionOS]${NC} Services started."
        ;;
    stop)
        echo -e "${BLUE}[HyperionOS]${NC} Stopping services..."
        sudo systemctl stop hyperion.service
        echo -e "${RED}[HyperionOS]${NC} Engine service stopped."
        ;;
    restart)
        echo -e "${BLUE}[HyperionOS]${NC} Restarting services..."
        sudo systemctl restart hyperion.service nginx
        echo -e "${GREEN}[HyperionOS]${NC} Services restarted."
        ;;
    reload)
        echo -e "${BLUE}[HyperionOS]${NC} Reloading Nginx & PHP-FPM..."
        sudo systemctl reload nginx
        sudo systemctl restart php-fpm 2>/dev/null || sudo systemctl restart php*-fpm 2>/dev/null || true
        echo -e "${GREEN}[HyperionOS]${NC} Configuration reloaded."
        ;;
    status)
        echo -e "${BLUE}=== Hyperion Backend Engine Status ===${NC}"
        sudo systemctl status hyperion.service --no-pager
        echo -e "\n${BLUE}=== Nginx Web Server Status ===${NC}"
        sudo systemctl status nginx --no-pager
        ;;
    logs)
        echo -e "${BLUE}[HyperionOS]${NC} Streaming backend logs (Press Ctrl+C to stop)..."
        sudo journalctl -u hyperion.service -f
        ;;
    venv)
        echo -e "${BLUE}[HyperionOS]${NC} Entering virtual environment..."
        echo -e "${YELLOW}Type 'deactivate' to exit.${NC}"
        bash --rcfile <(echo "source /HyperionOS/venv/bin/activate")
        ;;
    *)
        echo -e "${GREEN}HyperionOS CLI Tool${NC}"
        echo "Usage: hyperion <command>"
        echo ""
        echo "Available commands:"
        echo "  start     Start backend engine & web server"
        echo "  stop      Stop backend engine"
        echo "  restart   Restart backend engine & web server"
        echo "  reload    Reload Nginx and PHP-FPM configuration"
        echo "  status    Check runtime status of core services"
        echo "  logs      Tail live application logs"
        echo "  venv      Spawn subshell inside Python virtualenv"
        echo ""
        ;;
esac
EOF

chmod +x "$CLI_FILE"
log_success "CLI tool installed successfully. Run 'hyperion' from anywhere."

# ------------------------------------------------------------------------------
# Installation Complete Summary
# ------------------------------------------------------------------------------
echo -e "\n${GREEN}======================================================${NC}"
echo -e " ${GREEN}HyperionOS installation completed successfully!${NC}"
echo -e " Root Path : $TARGET_DIR"
echo -e " Engine    : Running on 127.0.0.1:8000"
echo -e " Dashboard : http://$(hostname -I | awk '{print $1}')"
echo -e "${GREEN}======================================================${NC}\n"