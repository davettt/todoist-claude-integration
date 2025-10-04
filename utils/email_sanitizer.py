"""
Email content sanitization utilities
CRITICAL: All URLs and email addresses must be stripped before sending to Claude
"""

import re
from typing import Dict


def sanitize_email_content(email_text: str) -> str:
    """
    Remove all URLs and email addresses from email content.

    Security: Prevents malicious links from being processed or stored.
    No whitelisting - strip everything.

    Args:
        email_text: Raw email text content

    Returns:
        Sanitized text with URLs and emails removed
    """
    if not email_text:
        return ""

    # IMPORTANT: Process in this order to avoid partial replacements

    # 1. Remove all URLs with protocols FIRST (http://, https://, ftp://, etc.)
    email_text = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "[URL REMOVED]",
        email_text,
        flags=re.IGNORECASE,
    )

    # 2. Remove www. URLs without protocol
    email_text = re.sub(
        r"\bwww\.(?:[a-zA-Z0-9]|[$-_@.&+])+\.[a-zA-Z]{2,}\b",
        "[URL REMOVED]",
        email_text,
        flags=re.IGNORECASE,
    )

    # 3. Remove email addresses BEFORE bare domains (to avoid partial replacement)
    email_text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "[EMAIL REMOVED]",
        email_text,
    )

    # 4. Remove bare domains with common TLDs (catches domain.com style URLs)
    # Use negative lookbehind to not match if preceded by @ (already handled above)
    email_text = re.sub(
        r"(?<!@)\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:com|org|net|edu|gov|mil|co|io|ai|app|dev|xyz|info|biz|me|us|uk|au|ca|de|fr|jp|cn|in|br|ru|nl|se|no|dk|fi|be|ch|at|nz|sg|hk|tw|kr|my|th|vn|ph|id|za|mx|ar|cl|pe|ve|co\.uk|co\.nz|com\.au|co\.za|co\.in|co\.id)\b",
        "[URL REMOVED]",
        email_text,
        flags=re.IGNORECASE,
    )

    # 5. Remove angle brackets (often used in email headers)
    email_text = re.sub(r"[<>]", "", email_text)

    # 6. Final cleanup: remove any remaining @ symbols that might be orphaned
    # (from partial email removal)
    email_text = re.sub(r"@\[URL REMOVED\]", "[EMAIL REMOVED]", email_text)

    return email_text.strip()


def html_to_text(html_content: str) -> str:
    """
    Convert HTML email to plain text.

    Args:
        html_content: HTML email body

    Returns:
        Plain text version with formatting removed
    """
    if not html_content:
        return ""

    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "lxml")

        # Remove script and style elements
        for element in soup(["script", "style", "head", "title", "meta", "[document]"]):
            element.decompose()

        # Get text and clean up whitespace
        text = soup.get_text(separator="\n")

        # Clean up excessive whitespace
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(line for line in lines if line)

        # Collapse multiple blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text

    except ImportError:
        print(
            "⚠️ BeautifulSoup not installed. Install with: pip install beautifulsoup4 lxml"
        )
        # Fallback: basic HTML tag removal
        text = re.sub(r"<[^>]+>", "", html_content)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    except Exception as e:
        print(f"⚠️ Error converting HTML to text: {str(e)}")
        # Return original content if conversion fails
        return html_content


def extract_sender_info(from_header: str) -> Dict[str, str]:
    """
    Parse sender information from From header.

    Args:
        from_header: Email From header (e.g., "John Doe <john@example.com>")

    Returns:
        Dict with 'name' and 'email' keys
    """
    if not from_header:
        return {"name": "Unknown", "email": "unknown@unknown.com"}

    # Pattern: "Name" <email> or Name <email> or just email
    match = re.match(r'^"?([^"<]+)"?\s*<([^>]+)>$', from_header.strip())

    if match:
        return {"name": match.group(1).strip(), "email": match.group(2).strip()}
    else:
        # Just an email address
        email = from_header.strip()
        # Extract name from email (part before @)
        name = email.split("@")[0] if "@" in email else email
        return {"name": name, "email": email}


def is_content_safe(text: str) -> bool:
    """
    Verify that content has been properly sanitized.

    Args:
        text: Text to check

    Returns:
        True if no URLs or emails detected, False otherwise
    """
    if not text:
        return True

    # Check for URLs
    url_patterns = [
        r"http[s]?://",
        r"www\.",
        r"\b[a-z0-9-]+\.(?:com|org|net|edu|gov|io|ai|app)\b",
    ]

    for pattern in url_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False

    # Check for email addresses (but allow our [EMAIL REMOVED] marker)
    if re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}", text):
        # Make sure it's not just our marker
        if "[EMAIL REMOVED]" not in text:
            return False

    return True


def get_sanitization_summary(original: str, sanitized: str) -> Dict[str, any]:
    """
    Generate summary of what was sanitized.

    Args:
        original: Original text
        sanitized: Sanitized text

    Returns:
        Dict with counts of removed items
    """
    # Count URL removals
    url_count = sanitized.count("[URL REMOVED]")

    # Count email removals
    email_count = sanitized.count("[EMAIL REMOVED]")

    # Calculate character reduction
    char_reduction = len(original) - len(sanitized)

    return {
        "urls_removed": url_count,
        "emails_removed": email_count,
        "characters_reduced": char_reduction,
        "is_safe": is_content_safe(sanitized),
    }
