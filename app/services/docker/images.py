from .client import get_docker_client


def get_images():
    client = get_docker_client()
    if not client:
        return []
    try:
        images = client.images.list()
        result = []
        for img in images:
            clean_id = img.id.split(":")[1][:12] if ":" in img.id else img.short_id
            tags = img.tags if img.tags else ["<none>:<none>"]
            size_mb = round(img.attrs.get("Size", 0) / (1024 * 1024), 2)
            result.append(
                {
                    "id": clean_id,
                    "tags": tags,
                    "size": size_mb,
                    "created": img.attrs.get("Created", "")[:10],
                }
            )
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
