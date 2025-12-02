from app.constants.catalogs import ALLOWED_SECTIONS

DEFAULT_SECTIONS = ["popular", "trending", "topRated"]

def parse_sections(param_value: str | None):
    """
    Converts ?sections=popular,action → ["popular", "action"]
    Ensures only valid sections survive.
    """
    if not param_value:
        return DEFAULT_SECTIONS

    raw = [s.strip() for s in param_value.split(",") if s.strip()]
    raw.extend(DEFAULT_SECTIONS)

    raw = list(set(raw))
    
    valid = [s for s in raw if s in ALLOWED_SECTIONS]

    if not valid:
        return DEFAULT_SECTIONS

    return valid
