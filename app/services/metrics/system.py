import psutil
import platform
import time


def get_system_info():
    current_time = time.time()
    uptime_seconds = int(current_time - psutil.boot_time())
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    uptime_str = (
        f"{days}d {hours}h {minutes}m"
        if days > 0
        else f"{hours}h {minutes}m {seconds}s"
    )

    return {
        "os": platform.system(),
        "hostname": platform.node(),
        "uptime": uptime_str,
        "cpu_cores": psutil.cpu_count(logical=True),
        "process_count": len(psutil.pids()),
    }
