from fastapi import Form, UploadFile, File
from fastapi.responses import JSONResponse
from app.services import node
from . import router


@router.post("/api/add")
async def api_add(
    name: str = Form(...),
    source_type: str = Form(...),
    source_val: str = Form(""),
    source_file: UploadFile = File(None),
    env_content: str = Form(""),
    start_cmd: str = Form(...),
):
    res = node.add_project(
        name, source_type, source_val, source_file, env_content, start_cmd
    )
    return JSONResponse(res)


@router.post("/api/delete")
async def api_delete(name: str = Form(...)):
    res = node.delete_project(name)
    return JSONResponse(res)


@router.post("/api/modify")
async def api_modify(
    name: str = Form(...), pkg_action: str = Form(""), start_cmd: str = Form(...)
):
    projects = node.load_projects()
    proj = next((p for p in projects if p["name"] == name), None)
    if not proj:
        return JSONResponse({"success": False, "error": "Project not found"})

    proj_path = proj["path"]

    if start_cmd and start_cmd != proj["start_cmd"]:
        ecosystem_content = f"""module.exports = {{
  apps: [
    {{
      name: "{name}",
      script: "{start_cmd}",
      cwd: "{proj_path}",
      instances: "max",
      exec_mode: "cluster",
      env: {{
        NODE_ENV: "production",
      }}
    }}
  ]
}};
"""
        ecosystem_path = proj_path / "ecosystem.config.cjs"
        ecosystem_path.write_text(ecosystem_content)

        proj["start_cmd"] = start_cmd
        node.save_projects(projects)

    if pkg_action:
        node.run_cmd(f"cd {proj_path} && sudo npm i {pkg_action}")

    node.run_cmd(f"sudo pm2 restart {name} --update-env")
    return JSONResponse({"success": True})

@router.post("/api/action")
async def api_action(name: str = Form(...), action_type: str = Form(...)):
    valid_actions = ["start", "stop", "restart", "reload", "flush"]
    if action_type not in valid_actions:
        return JSONResponse({"success": False, "error": "Invalid action"})
    
    res = node.run_cmd(f"sudo pm2 {action_type} {name}")
    if not res["success"]:
         return JSONResponse({"success": False, "error": res["error"]})
         
    return JSONResponse({"success": True})