import shutil
from pathlib import Path
from .utils import run_cmd, load_projects, save_projects


def add_project(name, source_type, source_val, env_content, start_cmd):
    base_dir = Path("/var/www/nodes")
    base_dir.mkdir(parents=True, exist_ok=True)
    proj_dir = base_dir / name

    if proj_dir.exists():
        return {"success": False, "error": "Project with this name already exists."}

    if source_type == "git":
        res = run_cmd(f"git clone {source_val} {proj_dir}")
        if not res["success"]:
            return res
    elif source_type == "folder":
        if Path(source_val).exists():
            shutil.copytree(source_val, proj_dir)
        else:
            proj_dir.mkdir(parents=True, exist_ok=True)

    nm_dir = proj_dir / "node_modules"
    if nm_dir.exists():
        shutil.rmtree(nm_dir)

    if env_content:
        env_path = proj_dir / ".env"
        env_path.write_text(env_content)

    npm_res = run_cmd(f"cd {proj_dir} && sudo npm install")
    if not npm_res["success"]:
        return {"success": False, "error": f"Failed running npm i: {npm_res['error']}"}

    pm2_res = run_cmd(f"cd {proj_dir} && sudo pm2 start {start_cmd} --name {name}")
    if not pm2_res["success"]:
        return {"success": False, "error": f"Failed starting PM2: {pm2_res['error']}"}

    projects = load_projects()
    projects.append(
        {
            "name": name,
            "path": str(proj_dir),
            "start_cmd": start_cmd,
            "status": "online",
        }
    )
    save_projects(projects)

    return {"success": True}


def delete_project(name):
    projects = load_projects()
    proj = next((p for p in projects if p["name"] == name), None)
    if proj:
        run_cmd(f"pm2 delete {name}")
        shutil.rmtree(proj["path"], ignore_errors=True)
        projects = [p for p in projects if p["name"] != name]
        save_projects(projects)
    return {"success": True}
