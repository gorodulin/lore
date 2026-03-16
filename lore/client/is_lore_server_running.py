import os
import socket


def is_lore_server_running(socket_path: str) -> bool:
    """Check if a lore server is connectable at socket_path."""
    if not os.path.exists(socket_path):
        return False
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect(socket_path)
        sock.close()
        return True
    except (ConnectionRefusedError, FileNotFoundError, OSError):
        return False
