import re

def clean_text(text: str) -> str:
    """
    Cleans raw extracted PDF text while preserving meaningful structure,
    such as section numbers (e.g. 3.1, Rule 4.2), headings, bullet points,
    and regulation references.
    """
    if not text:
        return ""

    # Replace null bytes and non-printable control characters (except newline, tab)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Fix broken hyphenated words across lines (e.g., "regula-\ntion" -> "regulation")
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # Replace non-breaking spaces and irregular unicode spaces with standard space
    text = re.sub(r"[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]", " ", text)

    # Collapse horizontal spaces/tabs into single space per line
    lines = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)

    # Rejoin lines, collapsing more than two consecutive newlines into two
    joined = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", joined)

    return cleaned.strip()
