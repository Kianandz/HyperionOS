from .client import get_docker_client


def list_containers():
    client = get_docker_client()
    if not client:
        return []
    containers = client.containers.list(all=True)
    result = []
    for c in containers:
        ports = c.attrs.get("NetworkSettings", {}).get("Ports", {})
        host_port = ""
        if ports:
            for c_port, h_ports in ports.items():
                if h_ports:
                    host_port = h_ports[0]["HostPort"]
                    break

        image_name = c.image.tags[0] if c.image.tags else c.image.id[:12]
        icon_url = f"https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/{image_name.split(':')[0].split('/')[-1]}.png"

        result.append(
            {
                "id": c.short_id,
                "name": c.name,
                "image": image_name,
                "status": c.status,
                "created": c.attrs["Created"][:10],
                "port": host_port,
                "icon": icon_url,
            }
        )
    return result


def get_container_details(container_id: str):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}
    try:
        c = client.containers.get(container_id)
        cfg = c.attrs.get("Config", {})
        host_cfg = c.attrs.get("HostConfig", {})
        ip_addr = "N/A"
        net_settings = c.attrs.get("NetworkSettings", {})
        if net_settings:
            ip_addr = net_settings.get("IPAddress", "")
            if not ip_addr and net_settings.get("Networks"):
                first_net = list(net_settings.get("Networks").values())[0]
                ip_addr = first_net.get("IPAddress", "N/A")

        raw_ports = c.attrs.get("NetworkSettings", {}).get("Ports", {}) or {}
        formatted_ports = []
        for c_port, h_ports in raw_ports.items():
            if h_ports:
                port_num, protocol = (
                    c_port.split("/") if "/" in c_port else (c_port, "tcp")
                )
                for hp in h_ports:
                    formatted_ports.append(
                        {
                            "container": port_num,
                            "protocol": protocol,
                            "host": hp.get("HostPort", ""),
                        }
                    )

        return {
            "id": c.short_id,
            "name": c.name,
            "image": cfg.get("Image"),
            "status": c.status,
            "ip": ip_addr,
            "created": c.attrs.get("Created", "")[:19].replace("T", " "),
            "env": cfg.get("Env", []),
            "volumes": host_cfg.get("Binds", []),
            "ports": formatted_ports,
            "cmd": cfg.get("Cmd", []),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_container_logs(container_id: str):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}
    try:
        c = client.containers.get(container_id)
        logs = c.logs(tail=50).decode("utf-8")
        return {"status": "success", "logs": logs}
    except Exception as e:
        return {"status": "error", "message": str(e)}
