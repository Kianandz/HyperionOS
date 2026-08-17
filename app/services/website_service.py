import os
import subprocess
from jinja2 import Template

NGINX_CONF_DIR = "/etc/nginx/conf.d"

NGINX_TEMPLATE = """
server {
    listen 80;
    server_name {{ domain }};
    client_max_body_size {{ max_body_size }};

    {% if site_type == 'proxy' %}
    location / {
        proxy_pass http://127.0.0.1:{{ port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    {% elif site_type == 'php' %}
    root {{ root_dir }};
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass unix:{{ php_sock }};
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
    {% else %}
    root {{ root_dir }};
    index index.html index.htm;

    location / {
        try_files $uri $uri/ =404;
    }
    {% endif %}
}
"""

def get_service_status(service_name: str) -> dict:
    """Cek status service systemd (active, inactive, not_installed)."""
    try:
        res = subprocess.run(["systemctl", "is-active", service_name], capture_output=True, text=True)
        status = res.stdout.strip()
        
        check_exist = subprocess.run(["systemctl", "status", service_name], capture_output=True, text=True)
        is_installed = "loaded" in check_exist.stdout or "loaded" in check_exist.stderr

        return {
            "service": service_name,
            "status": status if is_installed else "not_installed",
            "is_active": status == "active"
        }
    except Exception:
        return {"service": service_name, "status": "unknown", "is_active": False}

def control_nginx(action: str):
    """Jalankan reload, restart, start, atau stop pada Nginx."""
    allowed_actions = ["reload", "restart", "start", "stop"]
    if action not in allowed_actions:
        raise Exception("Aksi Nginx tidak valid")

    try:
        subprocess.run(["sudo", "systemctl", action, "nginx"], check=True, capture_output=True, text=True)
        return {"status": "success", "message": f"Nginx berhasil di-{action}!"}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Gagal {action} Nginx: {e.stderr or e.stdout}")

def get_active_php_socket():
    """Cari lokasi socket PHP-FPM di sistem secara otomatis."""
    possible_sockets = [
        "/run/php-fpm/php-fpm.sock",
        "/run/php/php-fpm.sock",
        "/var/run/php-fpm/php-fpm.sock"
    ]
    for sock in possible_sockets:
        if os.path.exists(sock):
            return sock
    return "/run/php-fpm/php-fpm.sock"

def has_php_files(root_dir: str) -> bool:
    """Deteksi jika ada file .php di folder document root."""
    if not os.path.exists(root_dir):
        return False
    try:
        for file in os.listdir(root_dir):
            if file.endswith('.php'):
                return True
    except Exception:
        pass
    return False

def list_websites():
    sites = []
    if os.path.exists(NGINX_CONF_DIR):
        for filename in os.listdir(NGINX_CONF_DIR):
            if filename.endswith(".conf") or filename.endswith(".disabled"):
                is_active = filename.endswith(".conf")
                domain = filename.replace(".conf", "").replace(".disabled", "")
                sites.append({
                    "domain": domain,
                    "filename": filename,
                    "is_active": is_active
                })
    return sites

def get_website_config(domain: str):
    conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
    disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")
    
    target_path = conf_path if os.path.exists(conf_path) else disabled_path
    if not os.path.exists(target_path):
        raise Exception("File konfigurasi tidak ditemukan.")

    with open(target_path, "r") as f:
        return f.read()

def save_website(domain: str, mode: str, site_type: str = "proxy", port: int = 8000, 
                 root_dir: str = "/var/www/html", php_sock: str = "/run/php-fpm/php-fpm.sock", 
                 max_body_size: str = "64M", raw_config: str = ""):
    
    os.makedirs(NGINX_CONF_DIR, exist_ok=True)
    conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
    disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")

    # AUTO DETECT PHP
    if mode == "simple":
        if site_type == "static" and has_php_files(root_dir):
            site_type = "php"

        if site_type == "php" and (not php_sock or not os.path.exists(php_sock)):
            php_sock = get_active_php_socket()

        template = Template(NGINX_TEMPLATE)
        config_content = template.render(
            domain=domain,
            site_type=site_type,
            port=port,
            root_dir=root_dir,
            php_sock=php_sock,
            max_body_size=max_body_size
        )
    else:
        config_content = raw_config

    target_path = conf_path if os.path.exists(conf_path) or not os.path.exists(disabled_path) else disabled_path

    try:
        with open(target_path, "w") as f:
            f.write(config_content)

        subprocess.run(["sudo", "nginx", "-t"], check=True, capture_output=True, text=True)
        subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Nginx Test Error: {e.stderr or e.stdout}")
    except Exception as e:
        raise Exception(str(e))

    return {"status": "success", "message": f"Config {domain} berhasil disimpan!"}

def toggle_website(domain: str):
    conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
    disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")

    if os.path.exists(conf_path):
        os.rename(conf_path, disabled_path)
        status = "disabled"
    elif os.path.exists(disabled_path):
        os.rename(disabled_path, conf_path)
        status = "enabled"
    else:
        raise Exception("Domain tidak ditemukan")

    subprocess.run(["sudo", "nginx", "-t"], check=True, capture_output=True, text=True)
    subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True, capture_output=True, text=True)
    return {"status": "success", "message": f"Status domain {domain} diubah jadi {status}"}

def delete_website(domain: str):
    conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
    disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")

    if os.path.exists(conf_path):
        os.remove(conf_path)
    elif os.path.exists(disabled_path):
        os.remove(disabled_path)

    subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True, capture_output=True, text=True)
    return {"status": "success", "message": f"Website {domain} berhasil dihapus"}

PHP_INI_PATHS = [
    "/etc/php/php.ini",          # Arch Linux (CachyOS)
    "/etc/php/8.3/fpm/php.ini",  # Ubuntu/Debian
    "/etc/php/8.2/fpm/php.ini",
    "/etc/php.ini"               # CentOS
]

def control_php_fpm(action: str):
    """Kontrol service php-fpm via systemctl."""
    allowed = ["reload", "restart", "start", "stop"]
    if action not in allowed:
        raise Exception("Aksi tidak valid")

    svc = "php-fpm"
    chk = subprocess.run(["systemctl", "status", "php-fpm"], capture_output=True, text=True)
    if "loaded" not in chk.stdout:
        for v in ["php8.3-fpm", "php8.2-fpm", "php8.1-fpm", "php-fpm"]:
            if "loaded" in subprocess.run(["systemctl", "status", v], capture_output=True, text=True).stdout:
                svc = v
                break

    try:
        subprocess.run(["sudo", "systemctl", action, svc], check=True, capture_output=True, text=True)
        return {"status": "success", "message": f"PHP-FPM ({svc}) berhasil di-{action}!"}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Gagal {action} PHP-FPM: {e.stderr or e.stdout}")

def get_service_logs(target: str, lines: int = 150):
    """Ambil log Nginx / PHP-FPM fleksibel (journalctl fallback ke file log)."""
    logs = ""
    
    # 1. Coba lewat journalctl dulu
    possible_units = {
        "nginx": ["nginx", "nginx.service"],
        "php": ["php-fpm", "php-fpm.service", "php8.3-fpm", "php8.2-fpm", "php81-php-fpm"]
    }
    
    units = possible_units.get(target, [target])
    
    for u in units:
        try:
            res = subprocess.run(
                ["sudo", "journalctl", "-u", u, "-n", str(lines), "--no-pager"],
                capture_output=True, text=True
            )
            # Kalau output journalctl ada isinya dan bukan pesan "No entries"
            if res.returncode == 0 and res.stdout.strip() and "No entries" not in res.stdout:
                return res.stdout
        except Exception:
            pass

    # 2. Fallback: Jika journalctl Not Found / Kosong, baca file log langsung dari /var/log/
    log_files = {
        "nginx": ["/var/log/nginx/error.log", "/var/log/nginx/access.log"],
        "php": [
            "/var/log/php-fpm/error.log", 
            "/var/log/php-fpm.log", 
            "/var/log/php8.3-fpm.log", 
            "/var/log/php8.2-fpm.log"
        ]
    }
    
    target_files = log_files.get(target, [])
    for file_path in target_files:
        if os.path.exists(file_path):
            try:
                res = subprocess.run(
                    ["sudo", "tail", "-n", str(lines), file_path],
                    capture_output=True, text=True
                )
                if res.returncode == 0 and res.stdout.strip():
                    return f"--- File Log: {file_path} ---\n\n" + res.stdout
            except Exception:
                pass

    return f"Log untuk {target} tidak ditemukan di journalctl maupun /var/log/."

def get_php_ini_path():
    for p in PHP_INI_PATHS:
        if os.path.exists(p):
            return p
    raise Exception("File php.ini tidak ditemukan!")

def read_php_config():
    path = get_php_ini_path()
    with open(path, "r") as f:
        return {"path": path, "config": f.read()}

def save_php_config(content: str):
    path = get_php_ini_path()
    try:
        with open(path, "w") as f:
            f.write(content)
        
        # Auto-reload biar config baru langsung ke-load
        control_php_fpm("reload")
        return {"status": "success", "message": "Konfigurasi php.ini berhasil disimpan!"}
    except Exception as e:
        raise Exception(f"Gagal simpan php.ini: {str(e)}")