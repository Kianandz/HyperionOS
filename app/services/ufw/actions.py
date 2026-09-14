import subprocess


def ufw_action(
    command_type: str,
    port: str = "",
    proto: str = "tcp",
    action: str = "allow",
    direction: str = "incoming",
):
    try:
        base_cmd = ["sudo", "ufw"]
        cmd = []

        if command_type == "toggle_active":
            cmd = base_cmd + ["--force", action]
        elif command_type == "set_default":
            cmd = base_cmd + ["default", action, direction]
        elif command_type == "add_rule":
            if proto == "both":
                rule_target = port
            else:
                rule_target = f"{port}/{proto}" if port else action
            cmd = base_cmd + [action, rule_target]
        elif command_type == "delete_rule":
            cmd = base_cmd + ["delete", action, port]

        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"status": "success", "message": "Rule executed successfully!"}

    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else str(e)
        return {"status": "error", "message": f"UFW OS Error: {err_msg}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
