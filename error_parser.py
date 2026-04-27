import re

def parse_strict_violation(stderr_log: str) -> dict | None:
    """
    Parses Playwright stderr log to identify Strict Mode Violation errors.
    Pattern: strict mode violation: locator('...') resolved to X elements
    """
    # Regex searches for the selector inside locator() and the number of elements after 'resolved to'
    # Supports both single and double quotes in the selector
    pattern = r"strict mode violation: locator\(['\"](.+?)['\"]\)\s+resolved to\s+(\d+)\s+elements"
    
    match = re.search(pattern, stderr_log, re.IGNORECASE)
    
    if match:
        return {
            "selector": match.group(1),
            "count": int(match.group(2))
        }
    
    return None
