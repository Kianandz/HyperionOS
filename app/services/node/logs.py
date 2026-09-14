from .utils import run_cmd


def get_project_logs(name):
    res = run_cmd(f"pm2 logs {name} --lines 100 --nostream")
    return res.get("output", res.get("error", "No logs found."))
