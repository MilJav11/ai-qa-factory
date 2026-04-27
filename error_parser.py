import re

def parse_strict_violation(stderr_log: str) -> dict | None:
    """
    Parses Playwright stderr log to identify Strict Mode Violation errors.
    Pattern: strict mode violation: locator('...') resolved to X elements
    """
    # Regex hľadá selektor vnútri locator() a počet elementov po 'resolved to'
    # Podporuje jednoduché aj dvojité úvodzovky v selektore
    pattern = r"strict mode violation: locator\(['\"](.+?)['\"]\)\s+resolved to\s+(\d+)\s+elements"
    
    match = re.search(pattern, stderr_log, re.IGNORECASE)
    
    if match:
        return {
            "selector": match.group(1),
            "count": int(match.group(2))
        }
    
    return None
