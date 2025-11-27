def simple_mutate(text: str) -> str:
    """Apply simple text mutations to evade detection."""
    return text.replace(" ", " ").strip()
