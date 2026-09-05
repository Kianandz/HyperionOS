import os
import re
import subprocess
from jinja2 import Template

NGINX_CONF_DIR = "/etc/nginx/conf.d"

NGINX_TEMPLATE = r"""
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

PHP_INI_PATHS = [
    "/etc/php/php.ini",          # Arch Linux
    "/etc/php/8.3/fpm/php.ini",  # Ubuntu/Debian
    "/etc/php/8.2/fpm/php.ini",
    "/etc/php.ini"               # CentOS
]

def get_service_status(service_name: str) -> dict:
    try:
        res = subprocess.run([ "sudo", "systemctl", "is-active", service_name], capture_output=True, text=True)
        status = res.stdout.strip()
        check_exist = subprocess.run([ "sudo","systemctl", "status", service_name], capture_output=True, text=True)
        is_installed = "loaded" in check_exist.stdout or "loaded" in check_exist.stderr
        return {
            "service": service_name,
            "status": status if is_installed else "not_installed",
            "is_active": status == "active"
        }
    except Exception:
        return {"service": service_name, "status": "unknown", "is_active": False}

def control_nginx(action: str):
    allowed_actions = ["reload", "restart", "start", "stop"]
    if action not in allowed_actions:
        raise Exception("Action is not valid")
    try:
        subprocess.run(["sudo", "systemctl", action, "nginx"], check=True, capture_output=True, text=True)
        return {"status": "success", "message": f"Nginx : {action}!"}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed {action} Nginx: {e.stderr or e.stdout}")

def get_active_php_socket():
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
                
                # Baca config buat dapetin port
                port = "80"
                filepath = os.path.join(NGINX_CONF_DIR, filename)
                try:
                    with open(filepath, "r") as f:
                        match = re.search(r'listen\s+(\d+)', f.read())
                        if match: port = match.group(1)
                except: pass

                sites.append({
                    "domain": domain,
                    "filename": filename,
                    "port": port,
                    "is_active": is_active
                })
    return sites

def get_website_config(domain: str):
    conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
    disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")
    target_path = conf_path if os.path.exists(conf_path) else disabled_path

    if not os.path.exists(target_path):
        raise Exception("Configuration not found!")

    with open(target_path, "r") as f:
        return f.read()

def save_website(domain: str, mode: str, site_type: str = "proxy", port: int = 8000, 
                 root_dir: str = "/var/www/html", php_sock: str = "/run/php-fpm/php-fpm.sock", 
                 max_body_size: str = "64M", raw_config: str = ""):
    
    os.makedirs(NGINX_CONF_DIR, exist_ok=True)
    
    new_domain = domain
    if mode != "simple" and raw_config:
        match_server = re.search(r'server_name\s+([^;]+);', raw_config)
        if match_server:
            new_domain = match_server.group(1).split()[0].strip()
            raw_config = re.sub(r'root\s+/var/www/html/[^;]+;', f'root /var/www/html/{new_domain};', raw_config)

    old_conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
    old_disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")
    
    new_conf_path = os.path.join(NGINX_CONF_DIR, f"{new_domain}.conf")
    new_disabled_path = os.path.join(NGINX_CONF_DIR, f"{new_domain}.disabled")

    if mode == "simple":
        if site_type == "static" and has_php_files(root_dir):
            site_type = "php"
        if site_type == "php" and (not php_sock or not os.path.exists(php_sock)):
            php_sock = get_active_php_socket()

        template = Template(NGINX_TEMPLATE)
        config_content = template.render(domain=new_domain, site_type=site_type, port=port, root_dir=root_dir, php_sock=php_sock, max_body_size=max_body_size)
    else:
        config_content = raw_config

    # Action Rename File & Folder kalau nama berubah
    if new_domain != domain:
        if os.path.exists(old_conf_path):
            os.rename(old_conf_path, new_conf_path)
        elif os.path.exists(old_disabled_path):
            os.rename(old_disabled_path, new_disabled_path)
        
        old_dir = f"/var/www/html/{domain}"
        new_dir = f"/var/www/html/{new_domain}"
        if os.path.exists(old_dir) and not os.path.exists(new_dir):
            os.rename(old_dir, new_dir)

    target_path = new_conf_path if os.path.exists(new_conf_path) or not os.path.exists(new_disabled_path) else new_disabled_path

    try:
        with open(target_path, "w") as f:
            f.write(config_content)
        subprocess.run(["sudo", "nginx", "-t"], check=True, capture_output=True, text=True)
        subprocess.run(["sudo", "systemctl", "reload-or-restart", "nginx"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # Revert / balikin nama file & folder kalau config nginx error biar ga rusak
        if new_domain != domain:
            if os.path.exists(new_conf_path): os.rename(new_conf_path, old_conf_path)
            elif os.path.exists(new_disabled_path): os.rename(new_disabled_path, old_disabled_path)
            if os.path.exists(f"/var/www/html/{new_domain}"): os.rename(f"/var/www/html/{new_domain}", f"/var/www/html/{domain}")
        raise Exception(f"Nginx Test Error: {e.stderr or e.stdout}")
    except Exception as e:
        raise Exception(str(e))

    return {"status": "success", "message": f"Config {new_domain} saved!"}

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
        raise Exception("Domain not found!")

    try:
        # Pake sudo dan reload-or-restart
        subprocess.run(["sudo", "nginx", "-t"], check=True, capture_output=True, text=True)
        subprocess.run(["sudo", "systemctl", "reload-or-restart", "nginx"], check=True, capture_output=True, text=True)
        return {"status": "success", "message": f"Status domain {domain} change to {status}"}
    except subprocess.CalledProcessError as e:
        # Biar kalau gagal, log error-nya ketangkep di GUI dan gak langsung 500
        raise Exception(f"Toggle Error: {e.stderr or e.stdout}")

def delete_website(domain: str):
    conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
    disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")

    if os.path.exists(conf_path):
        os.remove(conf_path)
    elif os.path.exists(disabled_path):
        os.remove(disabled_path)

    subprocess.run([ "sudo", "systemctl", "reload", "nginx"], check=True, capture_output=True, text=True)
    return {"status": "success", "message": f"Website {domain} deleted"}

def control_php_fpm(action: str):
    allowed = ["reload", "restart", "start", "stop"]
    if action not in allowed:
        raise Exception("Actions is not valid")

    svc = "php-fpm"
    chk = subprocess.run(["sudo", "systemctl", "status", "php-fpm"], capture_output=True, text=True)
    if "loaded" not in chk.stdout:
        for v in ["php8.3-fpm", "php8.2-fpm", "php8.1-fpm", "php-fpm"]:
            if "loaded" in subprocess.run(["sudo", "systemctl", "status", v], capture_output=True, text=True).stdout:
                svc = v
                break

    try:
        subprocess.run([ "sudo", "systemctl", action, svc], check=True, capture_output=True, text=True)
        return {"status": "success", "message": f"PHP-FPM ({svc}) : {action}!"}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed {action} PHP-FPM: {e.stderr or e.stdout}")

def get_service_logs(target: str, lines: int = 150):
    possible_units = {
        "nginx": ["nginx", "nginx.service"],
        "php": ["php-fpm", "php-fpm.service", "php8.3-fpm", "php8.2-fpm", "php81-php-fpm"]
    }
    units = possible_units.get(target, [target])
    
    for u in units:
        try:
            res = subprocess.run(
                [ "journalctl", "-u", u, "-n", str(lines), "--no-pager"],
                capture_output=True, text=True
            )
            if res.returncode == 0 and res.stdout.strip() and "No entries" not in res.stdout:
                return res.stdout
        except Exception:
            pass

    log_files = {
        "nginx": ["/var/log/nginx/error.log", "/var/log/nginx/access.log"],
        "php": ["/var/log/php-fpm/error.log", "/var/log/php-fpm.log", "/var/log/php8.3-fpm.log", "/var/log/php8.2-fpm.log"]
    }
    target_files = log_files.get(target, [])

    for file_path in target_files:
        if os.path.exists(file_path):
            try:
                res = subprocess.run(
                    [ "tail", "-n", str(lines), file_path],
                    capture_output=True, text=True
                )
                if res.returncode == 0 and res.stdout.strip():
                    return f"--- File Log: {file_path} ---\n\n" + res.stdout
            except Exception:
                pass

    return f"Log {target} not found in journalctl and /var/log/."

def get_php_ini_path():
    for p in PHP_INI_PATHS:
        if os.path.exists(p):
            return p
    raise Exception("php.ini not found!")

def read_php_config():
    path = get_php_ini_path()
    with open(path, "r") as f:
        return {"path": path, "config": f.read()}

def save_php_config(content: str):
    path = get_php_ini_path()
    try:
        with open(path, "w") as f:
            f.write(content)
        control_php_fpm("reload")
        return {"status": "success", "message": "Config php.ini saved!"}
    except Exception as e:
        raise Exception(f"Failed to save php.ini: {str(e)}")