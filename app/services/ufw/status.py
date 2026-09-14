import subprocess
import re


def get_ufw_status():
    try:
        res = subprocess.run(
            ["sudo", "ufw", "status", "verbose"],
            capture_output=True,
            text=True,
            check=True,
        )
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
        lines = output.split("\n")
        is_rule_section = False

        for line in lines:
            if "To" in line and "Action" in line and "From" in line:
                is_rule_section = True
                continue

            if is_rule_section and line.strip():
                parts = re.split(r"\s{2,}", line.strip())
                if len(parts) >= 3:
                    rules.append({"to": parts[0], "action": parts[1], "from": parts[2]})
                else:
                    parts = re.split(r"\s+", line.strip())
                    if len(parts) >= 3:
                        rules.append(
                            {
                                "to": parts[0],
                                "action": " ".join(parts[1:-1]),
                                "from": parts[-1],
                            }
                        )

        return {
            "status": "active" if is_active else "inactive",
            "default_incoming": default_incoming,
            "default_outgoing": default_outgoing,
            "rules": rules,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "default_incoming": "unknown",
            "default_outgoing": "unknown",
            "rules": [],
        }
