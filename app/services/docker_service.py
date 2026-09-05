import docker
import os
import uuid
import subprocess
import socket
import random

def get_docker_client():
    try:
        return docker.from_env()
    except Exception:
        return None

def get_docker_overview():
    client = get_docker_client()
    if not client:
        return {"status": "offline", "error": "Docker not running or permission denied"}
    try:
        info = client.info()
        return {
            "status": "online",
            "containers_running": info.get("ContainersRunning", 0),
            "containers_stopped": info.get("ContainersStopped", 0),
            "images_count": info.get("Images", 0),
            "docker_version": info.get("ServerVersion", "N/A")
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def list_containers():
    client = get_docker_client()
    if not client:
        return []
    containers = client.containers.list(all=True)
    result = []
    for c in containers:
        # Cari port yang di-mapping ke host
        ports = c.attrs.get('NetworkSettings', {}).get('Ports', {})
        host_port = ""
        if ports:
            for c_port, h_ports in ports.items():
                if h_ports:
                    host_port = h_ports[0]['HostPort']
                    break
        
        # Bikin icon default berdasarkan nama image (bisa di-custom nanti)
        image_name = c.image.tags[0] if c.image.tags else c.image.id[:12]
        icon_url = f"https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/{image_name.split(':')[0].split('/')[-1]}.png"

        result.append({
            "id": c.short_id,
            "name": c.name,
            "image": image_name,
            "status": c.status,  
            "created": c.attrs['Created'][:10],
            "port": host_port,
            "icon": icon_url
        })
    return result

def container_action(container_id: str, action: str, image_name: str = None):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}
    try:
        container = client.containers.get(container_id)
        if action == "start":
            container.start()
        elif action == "stop":
            container.stop()
        elif action == "restart":
            container.restart()
        elif action == "delete":
            container.remove(force=True)
        elif action == "uninstall_purge":
            # Hapus containernya dulu secara paksa
            container.remove(force=True)
            # Kalau ada nama imagenya, hapus juga imagenya
            if image_name:
                try:
                    client.images.remove(image=image_name, force=True)
                except Exception:
                    pass # Ignore error kalau image masih dipake container lain
                    
        return {"status": "success", "message": f"Action {action} on {container_id} Success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_container_details(container_id: str):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}
    try:
        c = client.containers.get(container_id)
        cfg = c.attrs.get('Config', {})
        host_cfg = c.attrs.get('HostConfig', {})
        ip_addr = "N/A"
        net_settings = c.attrs.get('NetworkSettings', {})
        if net_settings:
            ip_addr = net_settings.get('IPAddress', '')
            if not ip_addr and net_settings.get('Networks'):
                first_net = list(net_settings.get('Networks').values())[0]
                ip_addr = first_net.get('IPAddress', 'N/A')

        # --- TAMBAHKAN BAGIAN INI UNTUK FORMATTING PORT ---
        raw_ports = c.attrs.get('NetworkSettings', {}).get('Ports', {}) or {}
        formatted_ports = []
        for c_port, h_ports in raw_ports.items():
            if h_ports:
                # Pisahkan port dan protokol (misal '80/tcp' -> '80' dan 'tcp')
                port_num, protocol = c_port.split('/') if '/' in c_port else (c_port, 'tcp')
                for hp in h_ports:
                    formatted_ports.append({
                        "container": port_num,
                        "protocol": protocol,
                        "host": hp.get("HostPort", "")
                    })
        # ---------------------------------------------------

        return {
            "id": c.short_id,
            "name": c.name,
            "image": cfg.get('Image'),
            "status": c.status,
            "ip": ip_addr,
            "created": c.attrs.get('Created', '')[:19].replace('T', ' '),
            "env": cfg.get('Env', []), 
            "volumes": host_cfg.get('Binds', []), 
            "ports": formatted_ports, # <-- Gunakan array port yang sudah diformat
            "cmd": cfg.get('Cmd', [])
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_container_command(container_id: str, command: str):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}
    try:
        c = client.containers.get(container_id)
        exit_code, output = c.exec_run(command, tty=True)
        return {"status": "success", "output": output.decode('utf-8')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def install_and_run(data: dict):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}
    try:
        container = client.containers.run(
            data["image_name"],
            name=data.get("name"),
            ports=data.get("ports"),
            environment=data.get("env"),
            volumes=data.get("volumes"),
            network=data.get("network", "bridge"),
            detach=True
        )
        return {
            "status": "success", 
            "message": f"Successfully installed {data['image_name']}", 
            "container_id": container.short_id
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_container_logs(container_id: str):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}
    try:
        c = client.containers.get(container_id)
        logs = c.logs(tail=50).decode('utf-8')
        return {"status": "success", "logs": logs}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_images():
    client = get_docker_client()
    if not client:
        return []
    try:
        images = client.images.list()
        result = []
        for img in images:
            clean_id = img.id.split(':')[1][:12] if ':' in img.id else img.short_id
            tags = img.tags if img.tags else ["<none>:<none>"]
            size_mb = round(img.attrs.get('Size', 0) / (1024 * 1024), 2)
            result.append({
                "id": clean_id,
                "tags": tags,
                "size": size_mb,
                "created": img.attrs.get('Created', '')[:10]
            })
        return result
    except Exception:
        return []

def delete_image(image_id: str, force: bool = False):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker error"}
    try:
        client.images.remove(image=image_id, force=force)
        return {"status": "success", "message": f"Deleted {image_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def pull_image(image_name: str):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker error"}
    try:
        client.images.pull(image_name)
        return {"status": "success", "message": f"Pulled {image_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def export_container_compose(container_id: str):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker error"}
    try:
        c = client.containers.get(container_id)
        cfg = c.attrs.get('Config', {})
        host_cfg = c.attrs.get('HostConfig', {})
        
        name = c.name
        yaml = f"version: '3.8'\nservices:\n  {name}:\n    container_name: {name}\n    image: {cfg.get('Image', '')}\n"
        
        ports = c.attrs.get('NetworkSettings', {}).get('Ports', {})
        if ports:
            yaml += "    ports:\n"
            for c_port, h_ports in ports.items():
                if h_ports:
                    for hp in h_ports:
                        yaml += f"      - '{hp['HostPort']}:{c_port}'\n"
                        
        volumes = host_cfg.get('Binds', [])
        if volumes:
            yaml += "    volumes:\n"
            for vol in volumes:
                yaml += f"      - '{vol}'\n"
                
        env = cfg.get('Env', [])
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

def get_available_port(default_port: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Cek apakah port default kosong
        if s.connect_ex(('127.0.0.1', default_port)) != 0:
            return default_port
        
        # Kalau kepake, minta OS ngasih port kosong secara acak
        s.bind(('', 0))
        return s.getsockname()[1]

# Tambahin fungsi ini di docker_service.py
def update_container(data: dict):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}
    
    container_id = data.get("container_id")
    new_name = data.get("name")
    image = data.get("image")
    
    try:
        # 1. Cari container lama
        old_container = client.containers.get(container_id)
        
        # 2. Hancurkan container lama secara paksa
        old_container.remove(force=True)
        
        # 3. Setup Restart Policy buat Docker-py
        restart_policy = {"Name": data.get("restart_policy", "unless-stopped")}
        if restart_policy["Name"] == "no":
            restart_policy = {"Name": "no"}

        # 4. Bangun container baru
        new_container = client.containers.run(
            image,
            name=new_name,
            ports=data.get("ports", {}),
            environment=data.get("env", []),
            volumes=data.get("volumes", []),
            privileged=data.get("privileged", False),
            mem_limit=data.get("mem_limit", "1024m"),
            cpu_shares=data.get("cpu_shares", 1024),
            restart_policy=restart_policy,
            detach=True
        )
        
        return {
            "status": "success", 
            "message": f"Container {new_name} updated successfully", 
            "new_id": new_container.short_id
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Docker error pas recreate: {str(e)}"}