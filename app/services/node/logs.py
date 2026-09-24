import re
from .utils import run_cmd


def get_project_logs(name):
    res = run_cmd(f"sudo pm2 logs {name} --lines 100 --nostream --no-color")
    raw_output = res.get("output", res.get("error", "No logs found."))
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    clean_output = ansi_escape.sub("", raw_output)

    return clean_output
