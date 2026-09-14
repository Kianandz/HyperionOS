import subprocess


def set_samba_password(username: str, password: str):
    try:
        subprocess.run(
            ["sudo", "useradd", "-M", "-s", "/sbin/nologin", username], check=False
        )
        proc = subprocess.Popen(
            ["sudo", "smbpasswd", "-s", "-a", username],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        proc.communicate(input=f"{password}\n{password}\n")
    except Exception as e:
        pass


def get_samba_users():
    try:
        res = subprocess.run(["sudo", "pdbedit", "-L"], capture_output=True, text=True)
        users = []
        for line in res.stdout.splitlines():
            if ":" in line:
                users.append(line.split(":")[0])
        return users
    except Exception:
        return []


def delete_samba_user(username: str):
    subprocess.run(["sudo", "smbpasswd", "-x", username], check=False)
