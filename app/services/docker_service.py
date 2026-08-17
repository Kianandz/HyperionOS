import docker

def get_docker_client():

    """Menginisialisasi client Docker via local socket."""

    try:

        return docker.from_env()
    
    except Exception as e:

        return None

def get_docker_overview():

    client = get_docker_client()

    if not client:

        return {"status": "offline", "error": "Docker service tidak berjalan atau perizinan ditolak"}
    
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

        result.append({

            "id": c.short_id,

            "name": c.name,

            "image": c.image.tags[0] if c.image.tags else c.image.id[:12],

            "status": c.status,  

            "created": c.attrs['Created'][:10]

        })

    return result

def container_action(container_id: str, action: str):

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

        return {"status": "success", "message": f"Aksi {action} pada {container_id} berhasil"}
    
    except Exception as e:

        return {"status": "error", "message": str(e)}
    