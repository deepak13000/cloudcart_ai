import re

# ─────────────────────────────────────────────────────────────
#  INJECTION PATTERNS (CENTRALIZED)
# ─────────────────────────────────────────────────────────────

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?instructions?",
    r"forget\s+(everything|all)",
    r"act\s+as",
    r"you\s+are\s+now",
    r"pretend\s+to\s+be",
    r"reveal\s+(system\s+)?prompt",
    r"override",
    r"bypass",
    r"<\s*script",      # XSS
    r"\{\{.*\}\}",      # template injection
]


# ─────────────────────────────────────────────────────────────
#  FUNCTIONS
# ─────────────────────────────────────────────────────────────

def detect_prompt_injection(text: str) -> bool:
    """
    Returns True if suspicious pattern is found
    """
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def sanitize_input(text: str) -> str:
    """
    Basic sanitization (extend if needed)
    """
    text = text.strip()

    # remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text


def contains_pii(text: str) -> bool:
    """
    Detect basic PII patterns
    """
    patterns = [
        r"\b\d{16}\b",          # credit card
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{10}\b",          # phone (basic)
    ]

    for pattern in patterns:
        if re.search(pattern, text):
            return True

    return False