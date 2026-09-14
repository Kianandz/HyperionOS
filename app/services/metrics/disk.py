import psutil


def get_disk_info():
    disks = []
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append(
                {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "percent": usage.percent,
                }
            )
        except PermissionError:
            continue
    return disks
