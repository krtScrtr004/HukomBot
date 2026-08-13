from pathlib import Path
from fastapi import Request


def get_project_root(level: int = 4) -> Path:
    return Path(__file__).resolve().parents[level - 1]


def is_pdf(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except (FileNotFoundError, PermissionError):
        return False


def format_conversation_history(histories: list[dict[str, str]]) -> str:
    formatted_history = []
    for history in histories:
        role = history.get("role") or "unknown"
        context = history.get("context") or "Unknown context"

        formatted_history.append(f"Role: {role}\nContext: {context}")

    return "\n\n---\n\n".join(formatted_history)


def get_client_ip(request: Request, trusted_proxies: bool = True) -> str | None:
    """
    Retrieve the real client IP address from a FastAPI/Starlette request.

    Checks X-Forwarded-For and X-Real-IP headers when the app is behind
    a reverse proxy (nginx, load balancer, etc.), falling back to the
    direct socket peer address.

    Args:
        request: The incoming FastAPI request.
        trusted_proxies: Whether to trust forwarded headers. Set to False
            if the app is directly internet-facing (no proxy in front),
            since these headers can be spoofed by the client otherwise.

    Returns:
        The client's IP address as a string, or "unknown" if unresolvable.
    """
    if trusted_proxies:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # First entry in the chain is the original client
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

    if request.client:
        return request.client.host

    return None
