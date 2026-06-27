from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


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
