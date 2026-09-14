import psutil


def get_memory_info():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "ram": {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent,
        },
        "swap": {
            "total_gb": round(swap.total / (1024**3), 2),
            "used_gb": round(swap.used / (1024**3), 2),
            "percent": swap.percent,
        },
    }
