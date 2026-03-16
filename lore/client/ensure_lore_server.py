import fcntl
import os
import subprocess
import sys
import time

from lore.client.is_lore_server_running import is_lore_server_running


def ensure_lore_server(socket_path: str) -> bool:
    """Ensure a lore server is running and connectable.

    Uses a file lock to prevent concurrent startup races. Checks if
    the socket is live, removes stale sockets, and spawns a new server
    process if needed. Returns True if server is running.
    """
    if is_lore_server_running(socket_path):
        return True

    lock_path = socket_path.rsplit(".", 1)[0] + ".lock"
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)

    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        try:
            # Re-check after acquiring lock
            if is_lore_server_running(socket_path):
                return True

            if os.path.exists(socket_path):
                try:
                    os.remove(socket_path)
                except OSError:
                    pass

            _start_lore_server()
            return _wait_for_lore_server(socket_path, timeout=2.0)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
    except OSError:
        return False


def _start_lore_server() -> None:
    """Spawn lore-server as a detached background process."""
    subprocess.Popen(
        [sys.executable, "-m", "lore.server.cli.serve_lore"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _wait_for_lore_server(socket_path: str, timeout: float) -> bool:
    """Wait for the server to become connectable within timeout seconds."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if is_lore_server_running(socket_path):
            return True
        time.sleep(0.05)
    return False
