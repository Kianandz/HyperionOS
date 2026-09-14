# HyperionOS

> A lightweight, modern, and modular web-based server management panel built with FastAPI and Python for Linux environments.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Framework](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-f34b7d.svg)

---

## 📌 Overview

**HyperionOS** is an open-source, all-in-one Linux server administration dashboard. Designed to bridge the gap between command-line server operations and modern web interfaces, HyperionOS empowers system administrators and developers to monitor, configure, and manage core server infrastructure seamlessly through an intuitive browser interface.

---

## ✨ Key Features

### 🔒 PAM-Based Native Authentication
- Integrates directly with Linux Pluggable Authentication Modules (PAM).
- Secures panel access using system credentials without requiring separate user databases.

### 📊 System Health & Performance Monitoring
- Real-time telemetry for CPU usage, memory allocation, swap space, and disk utilization.
- Live process monitoring and system resource analytics.

### 🌐 Web Server & Reverse Proxy Manager
- Automated host and configuration management for **Nginx**, **PHP-FPM**, and **Node.js**.
- Easily create reverse proxies, configure virtual hosts, manage SSL certificates, and view live access/error logs.

### 🐳 Docker & Container Orchestration
- Complete interface for managing Docker containers, images, volumes, and networks.
- Full support for **Docker Compose** stack deployment and live container log streaming.

### 🗄️ Database Management (MySQL / MariaDB)
- Built-in GUI for local database administration.
- Execute custom SQL queries, perform table CRUD operations, inspect schemas, and manage user privileges.

### 📁 Advanced Web File Manager
- Feature-rich file browser supporting uploads, downloads, archive compression/extraction (ZIP/TAR), permission management (`chmod`/`chown`), and inline text editing.

### 🛡️ Firewall & Network Security (UFW)
- Graphical control for Uncomplicated Firewall (UFW).
- Add/remove TCP & UDP rules, toggle firewall statuses, and monitor security logs.

### ☁️ Cloudflare Tunnels Integration
- Manage `cloudflared` instances to securely expose local services to the web without opening public ports.

### 📂 Samba Network Sharing
- Graphical configuration for SMB/Samba local network shares.
- Set share paths, guest permissions, and manage Samba user passwords.

### 💻 Web-Based Interactive Terminal
- Full pseudo-terminal (PTY) emulation over WebSockets.
- Execute shell commands securely directly from your browser.

---

## 🏗️ Project Architecture

HyperionOS is built following modern software design patterns, separating routing, business logic, and OS-level execution:

```
hyperion-os/
├── app/
│   ├── core/           # Core configuration, security middleware & PAM auth handlers
│   │   ├── config.py
│   │   └── security.py
│   ├── routes/         # Modular API and HTML route controllers
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── database.py
│   │   ├── docker.py
│   │   ├── files.py
│   │   ├── firewall.py
│   │   ├── samba.py
│   │   ├── system.py
│   │   ├── terminal.py
│   │   └── webserver.py
│   ├── services/       # Service layer executing Linux system utilities & CLI commands
│   │   ├── docker_service.py
│   │   ├── system_service.py
│   │   └── ...
│   └── templates/      # Jinja2 HTML templates and Tailwind CSS UI layout
├── scripts/            # Deployment and operational helper scripts
├── install.sh          # One-click installation script
├── requirements.txt    # Python dependencies
├── main.py             # Application entry point
└── README.md
```

---

## ⚙️ Prerequisites

- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, or RHEL-based distributions recommended)
- **Python**: Python 3.10 or higher
- **Privileges**: `root` or `sudo` access (required for PAM authentication and `systemctl` interactions)
- **Dependencies**: `systemd`, `nginx` (optional), `docker` & `docker-compose` (optional)

---

## 🚀 Installation & Setup

### Automated Quick Installation

HyperionOS provides an automated installation script to set up system dependencies, virtual environments, and initial permissions automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/your-username/hyperion-os/main/install.sh | sudo bash
```

---

### Manual Installation

If you prefer to set up HyperionOS manually, follow these steps:

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/hyperion-os.git
cd hyperion-os
```

#### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
```

#### 5. Run the Application
Start the Uvicorn server:
```bash
python main.py
# or directly via Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Access the panel by navigating to `http://<your-server-ip>:8000`.

---

## 🛡️ Running as a Systemd Service

To ensure HyperionOS runs continuously in the background and starts automatically on system boot:

1. Create a service file at `/etc/systemd/system/hyperion.service`:

```ini
[Unit]
Description=HyperionOS Web Management Panel
After=network.target

[Service]
User=root
WorkingDirectory=/opt/hyperion-os
ExecStart=/opt/hyperion-os/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hyperion
sudo systemctl start hyperion
```

3. Check service status:
```bash
sudo systemctl status hyperion
```

---

## 🔒 Security & Best Practices

- **Reverse Proxy & SSL**: Always run HyperionOS behind Nginx, Caddy, or Cloudflare Tunnel with SSL/TLS enabled for secure traffic encryption.
- **Firewall Rules**: Restrict access to the application port using UFW or external security groups to trusted IP addresses only.
- **PAM Authorization**: Ensure that user access levels are strictly controlled via Linux system accounts.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
