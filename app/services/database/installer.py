import subprocess
import shutil


def check_mysql_installed() -> bool:
    return shutil.which("mysql") is not None or shutil.which("mysqld") is not None


def install_local_mysql():
    try:
        if shutil.which("apt"):
            pkg_mgr = "debian"
        elif shutil.which("pacman"):
            pkg_mgr = "arch"
        else:
            return {
                "status": "error",
                "message": "OS not supported! Only Debian/Ubuntu or Arch are supported.",
            }

        if pkg_mgr == "debian":
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "mysql-server"], check=True
            )
            service_name = "mysql"
        elif pkg_mgr == "arch":
            subprocess.run(
                ["sudo", "pacman", "-Sy", "--noconfirm", "mariadb"], check=True
            )
            subprocess.run(
                [
                    "sudo",
                    "mariadb-install-db",
                    "--user=mysql",
                    "--basedir=/usr",
                    "--datadir=/var/lib/mysql",
                ],
                check=True,
            )
            service_name = "mariadb"

        subprocess.run(["sudo", "systemctl", "start", service_name], check=True)
        subprocess.run(["sudo", "systemctl", "enable", service_name], check=True)

        return {
            "status": "success",
            "message": f"MySQL/MariaDB installed successfully on {pkg_mgr.capitalize()}!",
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to install MySQL: {str(e)}"}
