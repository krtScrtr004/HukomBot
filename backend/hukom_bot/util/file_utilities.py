import magic

def get_mime_type(content: bytes) -> str:
    return magic.from_buffer(content, mime=True)

def is_valid_file_type(content: bytes, allowed_file_types = []) -> bool:
    mime =  get_mime_type(content)
    return mime in allowed_file_types