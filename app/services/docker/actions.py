from .client import get_docker_client


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
            container.remove(force=True)
            if image_name:
                try:
                    client.images.remove(image=image_name, force=True)
                except Exception:
                    pass

        return {
            "status": "success",
            "message": f"Action {action} on {container_id} Success",
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
        return {"status": "success", "output": output.decode("utf-8")}
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
            detach=True,
        )
        return {
            "status": "success",
            "message": f"Successfully installed {data['image_name']}",
            "container_id": container.short_id,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_container(data: dict):
    client = get_docker_client()
    if not client:
        return {"status": "error", "message": "Docker client error"}

    container_id = data.get("container_id")
    new_name = data.get("name")
    image = data.get("image")

    try:
        old_container = client.containers.get(container_id)
        old_container.remove(force=True)

        restart_policy = {"Name": data.get("restart_policy", "unless-stopped")}
        if restart_policy["Name"] == "no":
            restart_policy = {"Name": "no"}

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
            detach=True,
        )

        return {
            "status": "success",
            "message": f"Container {new_name} updated successfully",
            "new_id": new_container.short_id,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Docker error during recreate: {str(e)}",
        }
