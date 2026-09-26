from uuid import UUID
from pathlib import Path
from fastapi import Request
from datetime import datetime, timedelta
from backend.hukom_bot.enum.date_range import DateRange
from backend.hukom_bot.schema.mixin import DateRangeableMixin


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


def generate_daily_token_quota_key(user_id: UUID) -> str:
    return f"token:user:{user_id}:daily"


def build_date_range_where_clause(
    column_name: str,
    date_rangeable: DateRangeableMixin,
    include_where: bool = False,
) -> str:
    prefix = " WHERE " if include_where else " AND "

    now = datetime.now()

    date_start = date_rangeable.date_start
    date_end = date_rangeable.date_end

    if date_rangeable.date_range is not None:
        date_range = date_rangeable.date_range.to_range(now)

        if date_range.start is None and date_range.end is None:
            return ""

        date_start = date_range.start
        date_end = date_range.end

    conditions: list[str] = []

    if date_start is not None:
        conditions.append(
            f"{column_name} >= '{date_start.isoformat()}'"
        )

    if date_end is not None:
        conditions.append(
            f"{column_name} < '{date_end.isoformat()}'"
        )

    if not conditions:
        return ""

    return prefix + " AND ".join(conditions)