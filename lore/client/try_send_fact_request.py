from lore.client.resolve_lore_socket_path import resolve_lore_socket_path
from lore.client.is_lore_server_running import is_lore_server_running
from lore.client.ensure_lore_server import ensure_lore_server
from lore.client.send_fact_request import send_fact_request


def try_send_fact_request(project_root: str, method: str, params: dict) -> dict | None:
    """Try sending a request to the lore server, auto-starting if needed.

    Returns the result dict on success, or None if the server cannot
    be reached even after attempting to start it.
    """
    try:
        socket_path = resolve_lore_socket_path()
        if not is_lore_server_running(socket_path):
            if not ensure_lore_server(socket_path):
                return None
        return send_fact_request(socket_path, method, params, timeout=3.0, project_root=project_root)
    except Exception:
        pass
    return None
