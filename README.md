<<<<<<< HEAD
# HyperionOS
A lightweight server control panel.
=======
<<<<<<< HEAD
# HyperionOS
A lightweight server control panel.
=======
# HyperionOS - System Control Panel & Core Engine

[![OS - Arch | Debian | Ubuntu](https://img.shields.io/badge/OS-Arch%20%7C%20Debian%20%7C%20Ubuntu-blue.svg)](https://linux.org)
[![Backend - FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Web Server - Nginx](https://img.shields.io/badge/Web%20Server-Nginx-009639.svg)](https://nginx.org/)

**HyperionOS** is a lightweight, web-based server management platform powered by a FastAPI (Python 3) backend engine and a PHP/HTML frontend. It is designed to simplify centralized infrastructure management, including Nginx web hosting, Docker containers, MariaDB databases, UFW firewall rules, Cloudflare Tunnels, and server file navigation.

---

## 🛠️ Tech Stack & Architecture

* **Backend Engine**: FastAPI (Python 3) served via Uvicorn
* **Frontend UI**: PHP & HTML/CSS/JS (Nginx + PHP-FPM)
* **Database Management**: MariaDB
* **Security & Networking**: UFW, Cloudflared Tunnel, Linux PAM Authentication
* **Containerization**: Docker API integration

---

## 📂 Project Directory Structure

.
├── app/                        # Python Backend Engine (FastAPI)
│   ├── api/                    # REST API Endpoint routes
│   │   ├── auth.py
│   │   ├── cloudflared.py
│   │   ├── dashboard.py
│   │   ├── databases.py
│   │   ├── docker.py
│   │   ├── files.py
│   │   ├── firewall.py
│   │   ├── settings.py
│   │   └── websites.py
│   ├── services/               # Core business logic & system wrappers
│   │   ├── cloudflared_service.py
│   │   ├── database_service.py
│   │   ├── docker_service.py
│   │   ├── files_service.py
│   │   ├── metrics.py
│   │   ├── pam_service.py
│   │   ├── ufw_service.py
│   │   └── website_service.py
│   └── main.py                 # FastAPI application entrypoint
│
├── html/                       # Frontend Web Interface (PHP & Static Assets)
│   ├── assets/                 # CSS, JavaScript, Fonts, and Vendor files
│   ├── includes/               # UI Components & View Layouts
│   │   ├── sections/           # Modular views (Docker, DB, Firewall, etc.)
│   │   └── sidebar.php
│   ├── dashboard.php
│   └── index.php
│
├── .gitignore
├── install.sh                  # Automated deployment script (Arch, Debian, Ubuntu)
├── uninstall.sh                # Clean uninstallation script
├── README.md
└── requirements.txt            # Python environment dependencies

---

## 🚀 Installation

System setup is automated via the `install.sh` script. It handles OS detection, missing package installation, Python virtual environment configuration, systemd service registration, Nginx reverse proxy configuration, and Hyperion CLI binary installation.

### System Requirements
* **Supported OS**: Arch Linux, Debian, or Ubuntu
* **Privileges**: Root / Sudo access required

### Quick Start

1. Clone the repository to your host server:
   git clone https://github.com/Kianandz/HyperionOS.git
   cd HyperionOS

2. Execute the installer script as root:
   chmod +x install.sh
   sudo ./install.sh

Upon completion, the application core will be deployed to `/HyperionOS`. The FastAPI backend engine binds internally to port `8000` and is reverse-proxied via Nginx on standard HTTP port `80`.

---

## 💻 CLI Helper (`hyperion`)

The installer configures the `hyperion` command-line utility for quick service lifecycle management directly from your terminal:

| Command | Description |
| :--- | :--- |
| `hyperion start` | Starts the backend engine and Nginx services |
| `hyperion stop` | Stops the backend engine service |
| `hyperion restart` | Restarts both backend engine and Nginx |
| `hyperion reload` | Reloads Nginx and PHP-FPM configurations |
| `hyperion status` | Checks runtime status for core application services |
| `hyperion logs` | Tails live journalctl logs from the backend engine |
| `hyperion venv` | Spawns a subshell inside the Python virtual environment |

---

## 🗑️ Uninstallation

To cleanly purge HyperionOS from your server without removing shared core dependencies (like Docker or MariaDB):

chmod +x uninstall.sh
sudo ./uninstall.sh
>>>>>>> 3904fd5 (setup project structure, install script, gitignore, and readme)
>>>>>>> 3257dd4 (feat: initial setup)
