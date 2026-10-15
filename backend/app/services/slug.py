import re


def to_slug(value: str) -> str:
    """Lowercase, strip non [a-z0-9 -] chars, collapse whitespace/hyphens into single hyphens."""
    slug = value.strip().lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return re.sub(r"-+", "-", slug)
