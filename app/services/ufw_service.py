import subprocess
import re

def get_ufw_status():
    try:
        # Tambahin sudo di depan
        res = subprocess.run(["sudo", "ufw", "status", "verbose"], capture_output=True, text=True, check=True)
        output = res.stdout
        is_active = "Status: active" in output
        default_incoming = "deny"
        default_outgoing = "allow"

        default_match = re.search(r"Default:\s*([^\n]+)", output)
        if default_match:
            def_str = default_match.group(1)
            inc_match = re.search(r"(\w+)\s*\(incoming\)", def_str)
            out_match = re.search(r"(\w+)\s*\(outgoing\)", def_str)
            if inc_match:
                default_incoming = inc_match.group(1)
            if out_match:
                default_outgoing = out_match.group(1)

        rules = []
        lines = output.split('\n')
        is_rule_section = False

        for line in lines:
            if "To" in line and "Action" in line and "From" in line:
                is_rule_section = True
                continue

            if is_rule_section and line.strip():
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 3:
                    rules.append({"to": parts[0], "action": parts[1], "from": parts[2]})
                else:
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 3:
                        rules.append({"to": parts[0], "action": " ".join(parts[1:-1]), "from": parts[-1]})

        return {
            "status": "active" if is_active else "inactive",
            "default_incoming": default_incoming,
            "default_outgoing": default_outgoing,
            "rules": rules
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e), 
            "default_incoming": "unknown",
            "default_outgoing": "unknown",
            "rules": []
        }

def ufw_action(command_type: str, port: str = "", proto: str = "tcp", action: str = "allow", direction: str = "incoming"):
    try:
        base_cmd = ["sudo", "ufw"]
        cmd = []
        
        if command_type == "toggle_active":
            cmd = base_cmd + ["--force", action]
        elif command_type == "set_default":
            cmd = base_cmd + ["default", action, direction]
        elif command_type == "add_rule":
            # Kalau both, gak usah pake embel-embel /tcp atau /udp
            if proto == "both":
                rule_target = port
            else:
                rule_target = f"{port}/{proto}" if port else action
            cmd = base_cmd + [action, rule_target]
        elif command_type == "delete_rule":
            cmd = base_cmd + ["delete", action, port]
            
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"status": "success", "message": "Rule berhasil dieksekusi!"}
        
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else str(e)
        return {"status": "error", "message": f"UFW OS Error: {err_msg}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_ufw_logs(lines: int = 50):
    try:
        # Mengambil 50 baris terakhir dari /var/log/ufw.log (atau dmesg jika log file kosong/akses tertutup)
        cmd = ["sudo", "tail", "-n", str(lines), "/var/log/ufw.log"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        log_text = res.stdout.strip()
        if not log_text:
            log_text = "Belum ada log UFW"
            
        return {"status": "success", "logs": log_text}
    except Exception as e:
        return {"status": "error", "message": str(e), "logs": ""}