import os
import uuid
import subprocess
from .client import get_docker_client


def export_container_compose(container_id: str):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker error"}
    try:
        c = client.containers.get(container_id)
        cfg = c.attrs.get("Config", {})
        host_cfg = c.attrs.get("HostConfig", {})

        name = c.name
        yaml = f"version: '3.8'\nservices:\n  {name}:\n    container_name: {name}\n    image: {cfg.get('Image', '')}\n"

        ports = c.attrs.get("NetworkSettings", {}).get("Ports", {})
        if ports:
            yaml += "    ports:\n"
            for c_port, h_ports in ports.items():
                if h_ports:
                    for hp in h_ports:
                        yaml += f"      - '{hp['HostPort']}:{c_port}'\n"

        volumes = host_cfg.get("Binds", [])
        if volumes:
            yaml += "    volumes:\n"
            for vol in volumes:
                yaml += f"      - '{vol}'\n"

        env = cfg.get("Env", [])
        if env:
            yaml += "    environment:\n"
            for e in env:
                yaml += f"      - {e}\n"

        return {"status": "success", "compose": yaml}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def deploy_compose(yaml_data: str, project_name: str):
    tmp_dir = f"/tmp/hyperion_{uuid.uuid4().hex}"
    os.makedirs(tmp_dir, exist_ok=True)
    file_path = os.path.join(tmp_dir, "docker-compose.yml")
    try:
        with open(file_path, "w") as f:
            f.write(yaml_data)

        cmd = ["docker", "compose", "-f", file_path, "-p", project_name, "up", "-d"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return {"status": "error", "message": res.stderr}
        return {"status": "success", "message": f"Project {project_name} deployed!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
