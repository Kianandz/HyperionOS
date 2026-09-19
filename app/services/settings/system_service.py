import subprocess
import psutil
import socket
import os


def update_resolv_conf(primary: str, secondary: str):
    resolv_content = f"nameserver {primary}\nnameserver {secondary}\n"
    p = subprocess.Popen(
        ["sudo", "tee", "/etc/resolv.conf"], stdin=subprocess.PIPE, text=True
    )
    p.communicate(input=resolv_content)


def vacuum_journal_logs():
    subprocess.run(["sudo", "journalctl", "--vacuum-size=50M"], check=True)


def get_network_info() -> dict:
    nm_check = subprocess.run(
        ["systemctl", "is-active", "NetworkManager"], capture_output=True, text=True
    )
    networkd_check = subprocess.run(
        ["systemctl", "is-active", "systemd-networkd"], capture_output=True, text=True
    )

    manager = "Unknown"
    if nm_check.stdout.strip() == "active":
        manager = "NetworkManager"
    elif networkd_check.stdout.strip() == "active":
        manager = "systemd-networkd"

    interfaces = []
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()

    for iface_name, iface_addrs in addrs.items():
        if iface_name == "lo":
            continue
        ip_addr = ""
        for addr in iface_addrs:
            if addr.family == socket.AF_INET:
                ip_addr = addr.address

        is_up = stats[iface_name].isup if iface_name in stats else False
        interfaces.append(
            {"name": iface_name, "ip": ip_addr, "status": "UP" if is_up else "DOWN"}
        )

    return {"manager": manager, "interfaces": interfaces}


def apply_network_config(interface: str, mode: str, ip_address: str, gateway: str):
    manager = get_network_info()["manager"]

    if manager == "NetworkManager":
        try:
            con_name_check = subprocess.run(
                ["nmcli", "-t", "-f", "NAME,DEVICE", "con", "show"],
                capture_output=True,
                text=True,
            )

            con_name = interface
            for line in con_name_check.stdout.strip().split("\n"):
                if line.endswith(f":{interface}"):
                    con_name = line.rsplit(":", 1)[0]
                    break

            if mode == "dhcp":
                subprocess.run(
                    [
                        "sudo",
                        "nmcli",
                        "con",
                        "mod",
                        con_name,
                        "ipv4.method",
                        "auto",
                        "ipv4.addresses",
                        "",
                        "ipv4.gateway",
                        "",
                    ],
                    check=False,
                )
            elif mode == "static" and ip_address:
                cmd = [
                    "sudo",
                    "nmcli",
                    "con",
                    "mod",
                    con_name,
                    "ipv4.method",
                    "manual",
                    "ipv4.addresses",
                    ip_address,
                ]
                if gateway:
                    cmd.extend(["ipv4.gateway", gateway])
                subprocess.run(cmd, check=False)

            subprocess.run(["sudo", "nmcli", "con", "down", con_name], check=False)
            subprocess.run(["sudo", "nmcli", "con", "up", con_name], check=False)

        except Exception as e:
            print(f"Failed to configure network: {e}")


def get_time_info() -> dict:
    tz_out = subprocess.run(
        ["timedatectl", "show", "-p", "Timezone", "--value"],
        capture_output=True,
        text=True,
    )
    ntp_out = subprocess.run(
        ["timedatectl", "show", "-p", "NTP", "--value"], capture_output=True, text=True
    )

    tz_list_out = subprocess.run(
        ["timedatectl", "list-timezones"], capture_output=True, text=True
    )

    return {
        "current_tz": tz_out.stdout.strip(),
        "ntp_active": ntp_out.stdout.strip() == "yes",
        "all_tz": tz_list_out.stdout.strip().split("\n"),
    }


def apply_time_config(timezone: str, ntp: str):
    ntp_bool = "true" if ntp == "on" else "false"
    subprocess.run(["sudo", "timedatectl", "set-ntp", ntp_bool], check=False)
    if timezone:
        subprocess.run(["sudo", "timedatectl", "set-timezone", timezone], check=False)


def get_system_users() -> list:
    users = []
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) > 2 and parts[2].isdigit():
                    uid = int(parts[2])
                    if 1000 <= uid < 65534:
                        users.append(parts[0])
    except Exception:
        pass
    return users


def change_user_password(username: str, new_password: str):
    if username in get_system_users():
        p = subprocess.Popen(["sudo", "chpasswd"], stdin=subprocess.PIPE, text=True)
        p.communicate(input=f"{username}:{new_password}\n")


def get_app_port() -> str:
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("PORT="):
                    return line.strip().split("=")[1]
    return "8000"


def update_app_port(new_port: str):
    env_path = ".env"
    lines = []
    found = False

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("PORT="):
            lines[i] = f"PORT={new_port}\n"
            found = True
            break

    if not found:
        lines.append(f"\nPORT={new_port}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)
