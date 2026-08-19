import subprocess
import re

def get_ufw_status():

    try:

        res = subprocess.run(["sudo", "ufw", "status", "verbose"], capture_output=True, text=True, check=True)

        output = res.stdout

        is_active = "Status: active" in output

        rules = []

        lines = output.split('\n')

        is_rule_section = False

        for line in lines:

            if "To" in line and "Action" in line and "From" in line:

                is_rule_section = True

                continue

            if is_rule_section and line.strip():
                
                parts = re.split(r'\s+', line.strip())

                if len(parts) >= 3:

                    rules.append({

                        "to": parts[0],

                        "action": parts[1],

                        "from": parts[2]

                    })

        return {

            "status": "active" if is_active else "inactive",

            "rules": rules

        }
    
    except Exception as e:

        return {"status": "error", "message": str(e), "rules": []}

def ufw_action(command_type: str, port: str = "", proto: str = "tcp", action: str = "allow"):

    try:

        if command_type == "toggle_active":

            subprocess.run(["sudo", "ufw", action], check=True)

        elif command_type == "add_rule":

            rule_target = f"{port}/{proto}" if port else action

            subprocess.run(["sudo", "ufw", action, rule_target], check=True)

        elif command_type == "delete_rule":

            rule_target = f"{port}/{proto}"

            subprocess.run(["sudo", "ufw", "delete", action, rule_target], check=True)
        
        return {"status": "success", "message": "UFW Executed"}
    
    except Exception as e:

        return {"status": "error", "message": str(e)}
    