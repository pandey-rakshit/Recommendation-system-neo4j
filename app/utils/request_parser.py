from app.constants.catalogs import ALLOWED_SECTIONS

DEFAULT_SECTIONS = ["popular", "trending", "topRated"]

def parse_sections(param_value: str | None):
    """
    Converts ?sections=popular,action → ["popular", "action"]
    Ensures only valid sections survive.
    """

    # No sections provided → use defaults
    print("param_value:", param_value)
    if not param_value:
        return DEFAULT_SECTIONS

    # Normalize input: split, strip, lowercase safety
    raw = [s.strip() for s in param_value.split(",") if s.strip()]

    # Keep only valid sections
    valid = [s for s in raw if s in ALLOWED_SECTIONS]

    # If user passed invalid or empty → fallback to defaults
    if not valid:
        return DEFAULT_SECTIONS

    return valid
