# HyperionOS - System Control Panel & Core Engine

[![OS - Arch | Debian | Ubuntu](https://img.shields.io/badge/OS-Arch%20%7C%20Debian%20%7C%20Ubuntu-blue.svg)](https://linux.org)
[![Backend - FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Web Server - Nginx](https://img.shields.io/badge/Web%20Server-Nginx-009639.svg)](https://nginx.org/)

**HyperionOS** is a lightweight, web-based server management platform powered by a FastAPI (Python 3) backend engine and a PHP/HTML frontend.

It is designed to simplify centralized infrastructure management, including:

* Nginx web hosting
* Docker containers
* MariaDB databases
* UFW firewall rules
* Cloudflare Tunnels
* Server file navigation

---

## 🛠️ Tech Stack & Architecture

* **Backend Engine**: FastAPI (Python 3) served via Uvicorn
* **Frontend UI**: PHP & HTML/CSS/JS served through Nginx + PHP-FPM
* **Database Management**: MariaDB
* **Security & Networking**: UFW, Cloudflared Tunnel, Linux PAM Authentication
* **Containerization**: Docker API integration

---

## 📂 Project Directory Structure

```text
.
├── app/                        # Python Backend Engine (FastAPI)
│   ├── api/                    # REST API endpoint routes
│   │   ├── auth.py
│   │   ├── cloudflared.py
│   │   ├── dashboard.py
│   │   ├── databases.py
│   │   ├── docker.py
│   │   ├── files.py
│   │   ├── firewall.py
│   │   ├── settings.py
│   │   └── websites.py
│   │
│   ├── services/               # Core business logic & system wrappers
│   │   ├── cloudflared_service.py
│   │   ├── database_service.py
│   │   ├── docker_service.py
│   │   ├── files_service.py
│   │   ├── metrics.py
│   │   ├── pam_service.py
│   │   ├── ufw_service.py
│   │   └── website_service.py
│   │
│   └── main.py                 # FastAPI application entrypoint
│
├── html/                       # Frontend Web Interface
│   ├── assets/                 # CSS, JavaScript, fonts, and vendor files
│   ├── includes/               # UI components & view layouts
│   │   ├── sections/           # Modular views (Docker, DB, Firewall, etc.)
│   │   └── sidebar.php
│   ├── dashboard.php
│   └── index.php
│
├── .gitignore
├── install.sh                  # Automated deployment script
├── uninstall.sh                # Clean uninstallation script
├── README.md
└── requirements.txt            # Python environment dependencies
```

---

## 🚀 Installation

System setup is automated via the `install.sh` script.

The installer handles:

* OS detection
* Required package installation
* Python virtual environment configuration
* systemd service registration
* Nginx reverse proxy configuration
* Hyperion CLI installation

### System Requirements

* **Supported OS**: Arch Linux, Debian, or Ubuntu
* **Privileges**: Root / sudo access required

### Quick Start

1. Clone the repository:

```bash
git clone https://github.com/Kianandz/HyperionOS.git
cd HyperionOS
```

2. Run the installer:

```bash
chmod +x install.sh
sudo ./install.sh
```

Upon completion, HyperionOS will be deployed to `/HyperionOS`.

The FastAPI backend engine runs internally on port `8000` and is reverse-proxied through Nginx on standard HTTP port `80`.

---

## 💻 CLI Helper

The installer configures the `hyperion` command-line utility for quick service lifecycle management.

| Command            | Description                                            |
| :----------------- | :----------------------------------------------------- |
| `hyperion start`   | Starts the backend engine and Nginx services           |
| `hyperion stop`    | Stops the backend engine service                       |
| `hyperion restart` | Restarts both the backend engine and Nginx             |
| `hyperion reload`  | Reloads Nginx and PHP-FPM configurations               |
| `hyperion status`  | Checks the runtime status of core application services |
| `hyperion logs`    | Tails live `journalctl` logs from the backend engine   |
| `hyperion venv`    | Opens a subshell inside the Python virtual environment |

---

## 🗑️ Uninstallation

To cleanly remove HyperionOS without removing shared dependencies such as Docker or MariaDB:

```bash
chmod +x uninstall.sh
sudo ./uninstall.sh
```