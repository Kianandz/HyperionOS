import psutil
import time
import platform
from typing import Dict, Any

_last_net_io = psutil.net_io_counters()

_last_net_time = time.time()

def get_system_metrics() -> Dict[str, Any]:

    global _last_net_io, _last_net_time

    current_time = time.time()

    memory = psutil.virtual_memory()

    swap = psutil.swap_memory()
    
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

                "percent": usage.percent

            })

        except PermissionError:

            continue

    current_net_io = psutil.net_io_counters()

    elapsed = max(current_time - _last_net_time, 1.0)
    
    bytes_sent = current_net_io.bytes_sent - _last_net_io.bytes_sent

    bytes_recv = current_net_io.bytes_recv - _last_net_io.bytes_recv
    
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

        "swap": {

            "total_gb": round(swap.total / (1024 ** 3), 2),

            "used_gb": round(swap.used / (1024 ** 3), 2),

            "percent": swap.percent

        },

        "disks": disks,

        "network": {

            "upload_kbps": round((bytes_sent / elapsed) / 1024, 2),

            "download_kbps": round((bytes_recv / elapsed) / 1024, 2)

        }
        
    }