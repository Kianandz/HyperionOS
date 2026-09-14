from typing import Dict, Any
from .system import get_system_info
from .cpu import get_cpu_info
from .memory import get_memory_info
from .disk import get_disk_info
from .network import get_network_info


def get_system_metrics() -> Dict[str, Any]:
    mem_info = get_memory_info()

    return {
        "status": "online",
        "system": get_system_info(),
        "cpu_percent": get_cpu_info(),
        "ram": mem_info["ram"],
        "swap": mem_info["swap"],
        "disks": get_disk_info(),
        "network": get_network_info(),
    }
