import psutil
import time

_last_net_io = psutil.net_io_counters()
_last_net_time = time.time()


def get_network_info():
    global _last_net_io, _last_net_time
    current_time = time.time()
    current_net_io = psutil.net_io_counters()

    elapsed = max(current_time - _last_net_time, 1.0)
    bytes_sent = current_net_io.bytes_sent - _last_net_io.bytes_sent
    bytes_recv = current_net_io.bytes_recv - _last_net_io.bytes_recv

    _last_net_io = current_net_io
    _last_net_time = current_time

    return {
        "upload_kbps": round((bytes_sent / elapsed) / 1024, 2),
        "download_kbps": round((bytes_recv / elapsed) / 1024, 2),
    }
