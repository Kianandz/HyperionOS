import docker
import socket


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
            "docker_version": info.get("ServerVersion", "N/A"),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_available_port(default_port: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", default_port)) != 0:
            return default_port

        s.bind(("", 0))
        return s.getsockname()[1]
