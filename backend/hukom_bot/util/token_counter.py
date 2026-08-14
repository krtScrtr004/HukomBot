import tiktoken


def estimate_text_tokens(text: str, model: str | None = None) -> int:
    try:
        encoding = tiktoken.encoding_for_model(model or "gpt-4o-mini")
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def estimate_chat_tokens(prompt: str, model: str | None = None) -> int:
    return estimate_text_tokens(prompt, model=model) + 8

