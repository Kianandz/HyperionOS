#!/bin/bash

# Warna untuk output terminal
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fungsi untuk menampilkan ASCII Art HyperionOS
show_ascii() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
 _   _                       _             ___  ____  
| | | |_   _ _ __   ___ _ __(_) ___  _ __ / _ \/ ___| 
| |_| | | | | '_ \ / _ \ '__| |/ _ \| '_ \ | | \___ \ 
|  _  | |_| | |_) |  __/ |  | | (_) | | | | |_| |___) |
|_| |_|\__, | .__/ \___|_|  |_|\___/|_| |_|\___/|____/ 
       |___/|_|                                        
EOF
    echo -e "${NC}"
    echo "======================================================"
    echo -e "${GREEN}          HyperionOS Installer - Tahap Awal${NC}"
    echo "======================================================"
    echo ""
}

# Fungsi untuk mendeteksi OS Family (Debian-based / Arch-based)
detect_os() {
    echo -e "${YELLOW}[*] Mendeteksi Sistem Operasi...${NC}"
    sleep 1

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        
        echo -e "[+] Nama OS: ${GREEN}$NAME${NC}"
        echo -e "[+] ID: ${GREEN}$ID${NC}"
        
        # Cek ID atau ID_LIKE untuk menentukan keluarga distro
        if [[ "$ID" == "debian" || "$ID_LIKE" == *"debian"* ]]; then
            echo -e "[+] Keluarga OS: ${CYAN}Debian-based (atau turunannya)${NC}\n"
            PACKAGE_MANAGER="apt"
        elif [[ "$ID" == "arch" || "$ID_LIKE" == *"arch"* ]]; then
            echo -e "[+] Keluarga OS: ${CYAN}Arch-based (atau turunannya)${NC}\n"
            PACKAGE_MANAGER="pacman"
        else
            echo -e "${RED}[!] Peringatan: OS ini bukan keluarga Debian atau Arch.${NC}"
            echo -e "${RED}[!] HyperionOS saat ini hanya mendukung Debian-based dan Arch-based.${NC}\n"
            exit 1
        fi
    else
        echo -e "${RED}[-] File /etc/os-release tidak ditemukan. Tidak dapat mendeteksi OS.${NC}"
        exit 1
    fi
}

# Fungsi untuk instalasi cloudflared (Layanan Eksternal)
install_cloudflared() {
    echo -e "${YELLOW}[*] Memeriksa layanan eksternal: cloudflared...${NC}"
    if command -v cloudflared &> /dev/null; then
        echo -e "${GREEN}[+] cloudflared sudah terinstal.${NC}"
    else
        echo -e "${YELLOW}[*] Menginstal cloudflared...${NC}"
        if [ "$PACKAGE_MANAGER" == "apt" ]; then
            # Menambahkan repositori resmi Cloudflare untuk apt
            sudo mkdir -p --mode=0755 /usr/share/keyrings
            curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
            echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
            sudo apt-get update -y
            sudo apt-get install -y cloudflared
        elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
            # Mengunduh binary langsung karena package resmi pacman tidak tersedia default/butuh AUR
            echo -e "${YELLOW}[*] Mengunduh binary cloudflared untuk Arch Linux...${NC}"
            curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
            sudo chmod +x cloudflared
            sudo mv cloudflared /usr/local/bin/cloudflared
        fi
        echo -e "${GREEN}[+] cloudflared berhasil diinstal.${NC}"
    fi
}

# Fungsi untuk cek dan instal dependencies
install_dependencies() {
    echo -e "${YELLOW}[*] Memulai pengecekan dan instalasi dependencies...${NC}"
    
    # Memastikan curl tersedia untuk instalasi cloudflared nanti
    DEPENDENCIES_DEBIAN="curl nginx php-fpm mysql-server ufw docker.io docker-compose-plugin libpam0g-dev"
    DEPENDENCIES_ARCH="curl nginx php-fpm mariadb ufw docker docker-compose"
    
    if [ "$PACKAGE_MANAGER" == "apt" ]; then
        echo -e "${CYAN}[*] Memperbarui repositori APT...${NC}"
        sudo apt-get update -y
        
        for pkg in $DEPENDENCIES_DEBIAN; do
            if dpkg -l | grep -qw "$pkg"; then
                echo -e "${GREEN}[+] $pkg sudah terinstal.${NC}"
            else
                echo -e "${YELLOW}[*] Menginstal $pkg...${NC}"
                sudo apt-get install -y "$pkg"
            fi
        done
        
    elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
        echo -e "${CYAN}[*] Memperbarui basis data PACMAN...${NC}"
        sudo pacman -Sy --noconfirm
        
        for pkg in $DEPENDENCIES_ARCH; do
            if pacman -Qs "^${pkg}$" > /dev/null; then
                echo -e "${GREEN}[+] $pkg sudah terinstal.${NC}"
            else
                echo -e "${YELLOW}[*] Menginstal $pkg...${NC}"
                sudo pacman -S --noconfirm "$pkg"
            fi
        done
    fi

    # Memanggil instalasi layanan eksternal
    install_cloudflared
    
    echo -e "${GREEN}[*] Seluruh proses instalasi dependencies selesai!${NC}"
}

show_ascii
detect_os
install_dependencies

echo -e "${CYAN}======================================================${NC}"
echo -e "${GREEN}      Tahap Awal Selesai. Sistem Siap Digunakan!${NC}"
echo -e "${CYAN}======================================================${NC}"