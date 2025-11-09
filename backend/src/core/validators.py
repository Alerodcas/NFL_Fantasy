import re


def validate_password(value: str, *, min_len: int = 8, max_len: int = 12, max_bytes: int = 72, require_alnum: bool = True) -> str:
    """Validate password according to project policy.

    Rules:
    - length between min_len and max_len (characters)
    - byte-length <= max_bytes (bcrypt limit)
    - if require_alnum: only A-Za-z0-9 allowed
    - must include at least one lowercase, one uppercase and one digit

    Raises ValueError with a helpful message on failure. Returns the original value on success.
    """
    if value is None:
        raise ValueError("Password is required")

    # bcrypt limit check
    if len(value.encode("utf-8")) > max_bytes:
        raise ValueError(f"Password is too long (max {max_bytes} bytes)")

    if len(value) < min_len or len(value) > max_len:
        raise ValueError(f"Password must be between {min_len} and {max_len} characters")

    if require_alnum and not re.fullmatch(r"[A-Za-z0-9]+", value):
        raise ValueError("Password must be alphanumeric (A-Z, a-z, 0-9)")

    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one digit")

    return value
