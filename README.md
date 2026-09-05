<div align="center">
  <h1>🚀 HyperionOS</h1>
  <p><b>Web-Based Server Management Panel</b></p>
  <p>Automated provisioning, service configuration, and web-based administration for modern Linux environments.</p>
</div>

---

## 📖 Overview

**HyperionOS** is a comprehensive, lightweight platform engineering solution designed to simplify server management. It provides a highly modular, Python-powered backend paired with an HTMX-driven frontend to manage your web server, databases, firewall, Docker containers, and Cloudflare tunnels seamlessly.

Designed specifically for **Debian** and **Arch Linux** based distributions, HyperionOS abstracts complex system administration tasks into an intuitive web interface and a robust CLI tool.

## ✨ Key Features

* 🌐 **Web Server Management**: Integrated Nginx and PHP-FPM configuration and management.
* 🐳 **Docker Integration**: Built-in container management, statistics tracking, and an "App Store" for rapid deployments.
* 🗄️ **Database Administration**: Native MariaDB integration with web-based workspace, querying, and table management.
* 🛡️ **Security & Firewall**: Visual UFW (Uncomplicated Firewall) management and rule configuration.
* ☁️ **Cloudflared Tunnels**: Integrated Cloudflare zero-trust tunnel configuration directly from the dashboard.
* 📁 **Advanced File Manager**: Web-based file explorer with batch actions, permissions handling, and editor.
* 📊 **System Telemetry**: Real-time server metrics (CPU, RAM, Disk, Network) on the dashboard.
* ⚡ **HTMX-Powered UI**: Blazing fast, SPA-like frontend without the heavy JavaScript frameworks.

## 🛠️ Technology Stack

* **Backend**: Python 3 (Virtual Environment isolated)
* **Frontend**: HTML5, CSS3, Vanilla JS, [HTMX](https://htmx.org/)
* **System Services**: Nginx, PHP-FPM, MariaDB, Docker, UFW, Systemd
* **Security**: PAM authentication, strict filesystem ACLs, dynamic sudoers.

## 🚀 Installation & Quick Start

HyperionOS comes with an automated bootstrap script (`install.sh`) that provisions the system, installs dependencies, creates isolated service accounts, and configures `systemd`.

### Prerequisites
* A fresh instance of **Debian/Ubuntu** or **Arch Linux**.
* Root or `sudo` privileges.

### Deployment

```bash
curl -sSL https://projecthyperion.my.id/script/install.sh | sudo bash || wget -qO- https://projecthyperion.my.id/script/install.sh | sudobash
```

##### OR

```bash
# 1. Clone the repository
git clone https://github.com/Kianandz/HyperionOS.git
cd HyperionOS

# 2. Run the bootstrap script
chmod +x install.sh scripts/*.sh
sudo ./install.sh
```

The installer will output connection instructions and start the background daemon automatically. 

## 💻 Command Line Interface (CLI)

HyperionOS includes a native `hyperion` CLI operator tool for rapid administrative actions directly from the terminal.

```bash
hyperion start                 # Bootstrap background service
hyperion stop                  # Terminate service layer
hyperion restart               # Power cycle the service
hyperion status                # Display system telemetry and logs
hyperion set-user <usr> <pwd>  # Rotate ownership and security contexts
hyperion log                   # Stream application trace logs
```

## 📂 Project Structure

HyperionOS follows a clean, modular architecture:

```text
HyperionOS/
├── app/
│   ├── core/         # App configuration & security policies
│   ├── routes/       # Endpoint definitions (Auth, Docker, Databases, etc.)
│   ├── services/     # Business logic & system interactions (UFW, PAM, Nginx)
│   ├── static/       # CSS, Fonts, and Vanilla/HTMX JavaScript assets
│   └── templates/    # Modular HTML components and layouts
├── install.sh        # Core bootstrap and provisioning orchestrator
├── main.py           # Application entry point
└── requirements.txt  # Python dependencies
```
