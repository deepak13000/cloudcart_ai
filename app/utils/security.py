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
    r"<\s*script",         # XSS
    r"\{\{.*\}\}",         # template injection
    r"jailbreak",
    r"DAN\s+mode",
    r"developer\s+mode",
]


def detect_prompt_injection(text: str) -> bool:
    """Returns True if a suspicious injection pattern is found."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def sanitize_input(text: str) -> str:
    """Strip and normalize whitespace."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def contains_pii(text: str) -> bool:
    """Detect basic PII patterns in output."""
    patterns = [
        r"\b\d{16}\b",             # credit card number
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{10}\b",             # phone number (basic)
    ]
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False


def is_simple_small_talk(text: str) -> bool:
    """Return True for short, generic small-talk queries."""
    normalized = re.sub(r"[^\w\s]", "", sanitize_input(text)).lower().strip()
    return normalized in {
        "hi",
        "hello",
        "hey",
        "hey there",
        "greetings",
        "good morning",
        "good afternoon",
        "good evening",
        "thanks",
        "thank you",
        "bye",
        "goodbye",
    }


def small_talk_response(text: str) -> str:
    """Return a canned local reply for small-talk or greeting inputs."""
    normalized = re.sub(r"[^\w\s]", "", sanitize_input(text)).lower().strip()
    if normalized in {"hi", "hello", "hey", "hey there", "greetings"}:
        return (
            "Hi there! I'm CloudCart AI. "
            "How can I help with your order, shipping, or product availability today?"
        )
    if normalized in {"good morning", "good afternoon", "good evening"}:
        return (
            "Hello! I'm CloudCart AI. "
            "Feel free to ask about orders, shipping, returns, or product availability."
        )
    if normalized in {"thanks", "thank you"}:
        return "You're welcome! Let me know if there's anything else I can help you with."
    if normalized in {"bye", "goodbye"}:
        return "Goodbye! If you need more help with CloudCart, just send another message."
    return "Hello! How can I help you with CloudCart today?"
