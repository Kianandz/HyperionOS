import os
import re
import subprocess
from jinja2 import Template
from .constants import NGINX_CONF_DIR, NGINX_ENABLED_DIR, IS_DEBIAN, NGINX_TEMPLATE
from .php import get_active_php_socket, has_php_files


def control_nginx(action: str):
    allowed_actions = ["reload", "restart", "start", "stop"]
    if action not in allowed_actions:
        raise Exception("Action is not valid")
    try:
        subprocess.run(
            ["sudo", "systemctl", action, "nginx"],
            check=True,
            capture_output=True,
            text=True,
        )
        return {"status": "success", "message": f"Nginx : {action}!"}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed {action} Nginx: {e.stderr or e.stdout}")


def list_websites():
    sites = []
    if os.path.exists(NGINX_CONF_DIR):
        for filename in os.listdir(NGINX_CONF_DIR):
            if IS_DEBIAN:
                if filename.endswith(".conf"):
                    domain = filename.replace(".conf", "")
                    is_active = os.path.exists(
                        os.path.join(NGINX_ENABLED_DIR, filename)
                    )
                else:
                    continue
            else:
                if filename.endswith(".conf") or filename.endswith(".disabled"):
                    is_active = filename.endswith(".conf")
                    domain = filename.replace(".conf", "").replace(".disabled", "")
                else:
                    continue

            port = "80"
            filepath = os.path.join(NGINX_CONF_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    match = re.search(r"listen\s+(\d+)", f.read())
                    if match:
                        port = match.group(1)
            except:
                pass

            sites.append(
                {
                    "domain": domain,
                    "filename": filename,
                    "port": port,
                    "is_active": is_active,
                }
            )
    return sites


def get_website_config(domain: str):
    if IS_DEBIAN:
        target_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
    else:
        conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
        disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")
        target_path = conf_path if os.path.exists(conf_path) else disabled_path

    if not os.path.exists(target_path):
        raise Exception("Configuration not found!")

    with open(target_path, "r") as f:
        return f.read()


def save_website(
    domain: str,
    mode: str,
    site_type: str = "proxy",
    port: int = 8000,
    root_dir: str = "/var/www/html",
    php_sock: str = "/run/php-fpm/php-fpm.sock",
    max_body_size: str = "64M",
    raw_config: str = "",
):
    os.makedirs(NGINX_CONF_DIR, exist_ok=True)
    if IS_DEBIAN:
        os.makedirs(NGINX_ENABLED_DIR, exist_ok=True)

    full_domain = domain.strip()
    safe_name = full_domain.split()[0].strip()

    if not root_dir or root_dir.strip() == "/var/www/html":
        root_dir = f"/var/www/html/{safe_name}"
        os.makedirs(root_dir, exist_ok=True)

    new_full_domain = full_domain
    new_safe_name = safe_name

    if mode != "simple" and raw_config:
        match_server = re.search(r"server_name\s+([^;]+);", raw_config)
        if match_server:
            new_full_domain = match_server.group(1).strip()
            new_safe_name = new_full_domain.split()[0].strip()

            # raw_config = re.sub(
            #     r"root\s+/var/www/html/[^;]+;",
            #     f"root /var/www/html/{new_safe_name};",
            #     raw_config,
            # )

    if mode == "simple":
        if site_type == "static" and has_php_files(root_dir):
            site_type = "php"
        if site_type == "php" and (not php_sock or not os.path.exists(php_sock)):
            php_sock = get_active_php_socket()

        template = Template(NGINX_TEMPLATE)
        config_content = template.render(
            domain=new_full_domain,
            site_type=site_type,
            port=port,
            root_dir=root_dir,
            php_sock=php_sock,
            max_body_size=max_body_size,
        )
    else:
        config_content = raw_config

    if IS_DEBIAN:
        old_conf_path = os.path.join(NGINX_CONF_DIR, f"{safe_name}.conf")
        new_conf_path = os.path.join(NGINX_CONF_DIR, f"{new_safe_name}.conf")
        old_enabled = os.path.join(NGINX_ENABLED_DIR, f"{safe_name}.conf")
        new_enabled = os.path.join(NGINX_ENABLED_DIR, f"{new_safe_name}.conf")

        was_active = os.path.exists(old_enabled) or (
            safe_name == new_safe_name and not os.path.exists(old_conf_path)
        )

        if new_safe_name != safe_name:
            if os.path.exists(old_conf_path):
                os.rename(old_conf_path, new_conf_path)
            if os.path.exists(old_enabled):
                os.remove(old_enabled)

            old_dir = f"/var/www/html/{safe_name}"
            new_dir = f"/var/www/html/{new_safe_name}"
            if os.path.exists(old_dir) and not os.path.exists(new_dir):
                os.rename(old_dir, new_dir)

        target_path = new_conf_path
    else:
        old_conf_path = os.path.join(NGINX_CONF_DIR, f"{safe_name}.conf")
        old_disabled_path = os.path.join(NGINX_CONF_DIR, f"{safe_name}.disabled")
        new_conf_path = os.path.join(NGINX_CONF_DIR, f"{new_safe_name}.conf")
        new_disabled_path = os.path.join(NGINX_CONF_DIR, f"{new_safe_name}.disabled")

        if new_safe_name != safe_name:
            if os.path.exists(old_conf_path):
                os.rename(old_conf_path, new_conf_path)
            elif os.path.exists(old_disabled_path):
                os.rename(old_disabled_path, new_disabled_path)

            old_dir = f"/var/www/html/{safe_name}"
            new_dir = f"/var/www/html/{new_safe_name}"
            if os.path.exists(old_dir) and not os.path.exists(new_dir):
                os.rename(old_dir, new_dir)

        target_path = (
            new_conf_path
            if os.path.exists(new_conf_path) or not os.path.exists(new_disabled_path)
            else new_disabled_path
        )

    try:
        with open(target_path, "w") as f:
            f.write(config_content)

        if IS_DEBIAN and was_active and not os.path.exists(new_enabled):
            os.symlink(target_path, new_enabled)

        subprocess.run(
            ["sudo", "nginx", "-t"], check=True, capture_output=True, text=True
        )
        subprocess.run(
            ["sudo", "systemctl", "reload-or-restart", "nginx"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        if new_safe_name != safe_name:
            if IS_DEBIAN:
                if os.path.exists(new_conf_path):
                    os.rename(new_conf_path, old_conf_path)
                if was_active:
                    if os.path.exists(new_enabled):
                        os.remove(new_enabled)
                    if not os.path.exists(old_enabled):
                        os.symlink(old_conf_path, old_enabled)
            else:
                if os.path.exists(new_conf_path):
                    os.rename(new_conf_path, old_conf_path)
                elif os.path.exists(new_disabled_path):
                    os.rename(new_disabled_path, old_disabled_path)

            if os.path.exists(f"/var/www/html/{new_safe_name}"):
                os.rename(
                    f"/var/www/html/{new_safe_name}", f"/var/www/html/{safe_name}"
                )
        raise Exception(f"Nginx Test Error: {e.stderr or e.stdout}")
    except Exception as e:
        raise Exception(str(e))

    return {"status": "success", "message": f"Config {new_full_domain} saved!"}


def toggle_website(domain: str):
    if IS_DEBIAN:
        conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
        enabled_path = os.path.join(NGINX_ENABLED_DIR, f"{domain}.conf")

        if not os.path.exists(conf_path):
            raise Exception("Domain not found!")

        if os.path.exists(enabled_path):
            os.remove(enabled_path)
            status = "disabled"
        else:
            os.symlink(conf_path, enabled_path)
            status = "enabled"
    else:
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
        subprocess.run(
            ["sudo", "nginx", "-t"], check=True, capture_output=True, text=True
        )
        subprocess.run(
            ["sudo", "systemctl", "reload-or-restart", "nginx"],
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "status": "success",
            "message": f"Status domain {domain} change to {status}",
        }
    except subprocess.CalledProcessError as e:
        raise Exception(f"Toggle Error: {e.stderr or e.stdout}")


def delete_website(domain: str):
    if IS_DEBIAN:
        conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
        enabled_path = os.path.join(NGINX_ENABLED_DIR, f"{domain}.conf")

        if os.path.exists(enabled_path):
            os.remove(enabled_path)
        if os.path.exists(conf_path):
            os.remove(conf_path)
    else:
        conf_path = os.path.join(NGINX_CONF_DIR, f"{domain}.conf")
        disabled_path = os.path.join(NGINX_CONF_DIR, f"{domain}.disabled")

        if os.path.exists(conf_path):
            os.remove(conf_path)
        elif os.path.exists(disabled_path):
            os.remove(disabled_path)

    subprocess.run(
        ["sudo", "systemctl", "reload", "nginx"],
        check=True,
        capture_output=True,
        text=True,
    )
    return {"status": "success", "message": f"Website {domain} deleted"}
