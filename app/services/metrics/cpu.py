import psutil


def get_cpu_info():
    return psutil.cpu_percent(interval=None)
