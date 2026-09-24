import shutil
import zipfile
import tempfile
import os
from pathlib import Path
from .utils import run_cmd, load_projects, save_projects


def add_project(name, source_type, source_val, source_file, env_content, start_cmd):
    base_dir = Path("/var/www/nodes")
    base_dir.mkdir(parents=True, exist_ok=True)
    proj_dir = base_dir / name

    if proj_dir.exists():
        return {"success": False, "error": "Project with this name already exists."}

    if source_type == "git":
        res = run_cmd(f"git clone {source_val} {proj_dir}")
        if not res["success"]:
            return res
    elif source_type == "upload":
        if source_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                shutil.copyfileobj(source_file.file, tmp)
                tmp_path = tmp.name

            try:
                with zipfile.ZipFile(tmp_path, "r") as zip_ref:
                    zip_ref.extractall(proj_dir)

                    extracted_items = list(proj_dir.iterdir())
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    inner_dir = extracted_items[0]
                    for item in inner_dir.iterdir():
                        shutil.move(str(item), str(proj_dir))
                    inner_dir.rmdir()

            except zipfile.BadZipFile:
                os.remove(tmp_path)
                return {
                    "success": False,
                    "error": "File Invalid!",
                }

            os.remove(tmp_path)
        else:
            return {"success": False, "error": "File not found!"}

    nm_dir = proj_dir / "node_modules"
    if nm_dir.exists():
        shutil.rmtree(nm_dir)

    if env_content:
        env_path = proj_dir / ".env"
        env_path.write_text(env_content)

    ecosystem_content = f"""module.exports = {{
  apps: [
    {{
      name: "{name}",
      script: "{start_cmd}",
      cwd: "{proj_dir}",
      instances: "max",
      exec_mode: "cluster",
      env: {{
        NODE_ENV: "production",
      }}
    }}
  ]
}};
"""
    ecosystem_path = proj_dir / "ecosystem.config.cjs"
    ecosystem_path.write_text(ecosystem_content)

    npm_res = run_cmd(f"cd {proj_dir} && sudo npm install")
    if not npm_res["success"]:
        return {"success": False, "error": f"Failed running npm i: {npm_res['error']}"}

    pm2_res = run_cmd(f"cd {proj_dir} && sudo pm2 start {ecosystem_path}")
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
        run_cmd(f"sudo pm2 delete {name}")
        shutil.rmtree(proj["path"], ignore_errors=True)
        projects = [p for p in projects if p["name"] != name]
        save_projects(projects)
    return {"success": True}
