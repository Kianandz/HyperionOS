import os
import glob
from .config import SHARE_CONF_DIR
from .core import init_samba_global, control_samba


def parse_smb_conf():
    init_samba_global()
    shares = []

    for conf_file in glob.glob(f"{SHARE_CONF_DIR}/*.conf"):
        name = os.path.basename(conf_file).replace(".conf", "")
        current = {
            "name": name,
            "path": "-",
            "guest_ok": "No",
            "writable": "No",
            "browseable": "Yes",
            "valid_users": "",
            "create_mask": "0755",
            "directory_mask": "0755",
            "raw": "",
        }

        with open(conf_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            current["raw"] = raw_content

            for line in raw_content.splitlines():
                line = line.strip()
                if "=" in line and not line.startswith(("#", "[", ";")):
                    k, v = [x.strip() for x in line.split("=", 1)]
                    k = k.lower()
                    if k == "path":
                        current["path"] = v
                    elif k in ["guest ok", "public"]:
                        current["guest_ok"] = "Yes" if v.lower() == "yes" else "No"
                    elif k in ["writable", "writeable"]:
                        current["writable"] = "Yes" if v.lower() == "yes" else "No"
                    elif k == "browseable":
                        current["browseable"] = "Yes" if v.lower() == "yes" else "No"
                    elif k == "valid users":
                        current["valid_users"] = v
                    elif k == "create mask":
                        current["create_mask"] = v
                    elif k == "directory mask":
                        current["directory_mask"] = v
        shares.append(current)
    return shares


def manage_smb_include(share_name: str, action: str):
    conf_path = "/etc/samba/smb.conf"
    include_line = f"include = {SHARE_CONF_DIR}/{share_name}.conf"

    try:
        with open(conf_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    if action == "add":
        lines = [
            l for l in lines if "include = /etc/samba/shares.conf.d/*.conf" not in l
        ]
        if not any(include_line in l for l in lines):
            lines.append(f"{include_line}\n")
    elif action == "remove":
        lines = [l for l in lines if include_line not in l]

    with open(conf_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def save_samba_share(
    name,
    path,
    guest_ok,
    writable,
    browseable,
    valid_users,
    create_mask,
    directory_mask,
    raw_config,
):
    os.makedirs(SHARE_CONF_DIR, exist_ok=True)
    conf_path = f"{SHARE_CONF_DIR}/{name}.conf"

    if raw_config and raw_config.strip():
        content = raw_config
    else:
        guest_val = "yes" if guest_ok else "no"
        write_val = "yes" if writable else "no"
        browse_val = "yes" if browseable else "no"

        content = f"[{name}]\n    path = {path}\n    public = {guest_val}\n    guest ok = {guest_val}\n    writable = {write_val}\n    browseable = {browse_val}\n"
        if create_mask:
            content += f"    create mask = {create_mask}\n"
        if directory_mask:
            content += f"    directory mask = {directory_mask}\n"
        if valid_users:
            content += f"    valid users = {valid_users}\n"
        else:
            if not guest_ok:
                content += f"    force user = root\n"

    with open(conf_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    manage_smb_include(name, "add")
    control_samba("restart")


def delete_samba_share(name: str):
    conf_path = f"{SHARE_CONF_DIR}/{name}.conf"
    if os.path.exists(conf_path):
        os.remove(conf_path)
    manage_smb_include(name, "remove")
    control_samba("restart")
