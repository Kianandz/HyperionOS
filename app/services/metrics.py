import psutil
import time
import platform

_last_net_io = psutil.net_io_counters()

_last_net_time = time.time()

def get_system_metrics():

    global _last_net_io, _last_net_time

    memory = psutil.virtual_memory()
    
    disks = []

    for partition in psutil.disk_partitions(all=False):

        try:

            usage = psutil.disk_usage(partition.mountpoint)

            disks.append({
                
                "device": partition.device,

                "mountpoint": partition.mountpoint,

                "fstype": partition.fstype,

                "total_gb": round(usage.total / (1024 ** 3), 2),

                "used_gb": round(usage.used / (1024 ** 3), 2),

                "free_gb": round(usage.free / (1024 ** 3), 2),

                "percent": usage.percent

            })

        except PermissionError:

            continue

    current_net_io = psutil.net_io_counters()

    current_time = time.time()
    
    elapsed = current_time - _last_net_time

    if elapsed <= 0:

        elapsed = 1.0

    bytes_sent = current_net_io.bytes_sent - _last_net_io.bytes_sent

    bytes_recv = current_net_io.bytes_recv - _last_net_io.bytes_recv
    
    upload_speed_kb = round((bytes_sent / elapsed) / 1024, 2)

    download_speed_kb = round((bytes_recv / elapsed) / 1024, 2)

    _last_net_io = current_net_io

    _last_net_time = current_time

    uptime_seconds = int(current_time - psutil.boot_time())

    days, remainder = divmod(uptime_seconds, 86400)

    hours, remainder = divmod(remainder, 3600)

    minutes, seconds = divmod(remainder, 60)

    uptime_str = f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m {seconds}s"

    return {

        "status": "online",

        "system": {

            "os": platform.system(),

            "hostname": platform.node(),

            "uptime": uptime_str,

            "cpu_cores": psutil.cpu_count(logical=True),

            "process_count": len(psutil.pids())

        },

        "cpu_percent": psutil.cpu_percent(interval=None),

        "ram": {

            "total_gb": round(memory.total / (1024 ** 3), 2),

            "used_gb": round(memory.used / (1024 ** 3), 2),

            "percent": memory.percent

        },

        "disks": disks,

        "network": {

            "upload_kbps": upload_speed_kb,

            "download_kbps": download_speed_kb

        }
        
    }