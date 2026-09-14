import subprocess


def get_ufw_logs(lines: int = 50):
    try:
        cmd = ["sudo", "tail", "-n", str(lines), "/var/log/ufw.log"]
        res = subprocess.run(cmd, capture_output=True, text=True)

        log_text = res.stdout.strip()
        if not log_text:
            log_text = "No UFW logs yet"

        return {"status": "success", "logs": log_text}
    except Exception as e:
        return {"status": "error", "message": str(e), "logs": ""}
