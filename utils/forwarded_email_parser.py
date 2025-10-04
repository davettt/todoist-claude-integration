"""
Forwarded Email Parser
Extracts original sender information from forwarded email bodies
"""

import re
from typing import Dict, Optional


def extract_original_sender(email_body: str) -> Optional[Dict[str, str]]:
    """
    Extract original sender from forwarded email body

    Args:
        email_body: The email body text

    Returns:
        Dict with 'name' and 'email' keys, or None if not found
    """
    if not email_body:
        return None

    # Common forwarded email patterns
    patterns = [
        # Gmail style: "---------- Forwarded message ---------\nFrom: Name <email>"
        r"(?:-+\s*Forwarded message\s*-+|Begin forwarded message:)\s*.*?From:\s*([^<\n]+?)\s*<([^>\n]+)>",
        # Outlook style: "From: Name <email>\nSent:"
        r"From:\s*([^<\n]+?)\s*<([^>\n]+)>\s*(?:Sent|Date):",
        # Any From: line with name and email in brackets (anywhere in email)
        r"From:\s*([^<\n]+?)\s*<([^>\n]+)>",
        # Just email in angle brackets
        r"From:\s*<([^>]+)>",
        # Email without brackets
        r"From:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,})",
    ]

    for pattern in patterns:
        match = re.search(pattern, email_body, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            groups = match.groups()

            if len(groups) == 2:
                # Has both name and email
                name = groups[0].strip().strip("\"'")
                email = groups[1].strip()
                return {"name": name, "email": email}
            elif len(groups) == 1:
                # Just email
                email = groups[0].strip()
                # Extract name from email (part before @)
                name = email.split("@")[0].replace(".", " ").title()
                return {"name": name, "email": email}

    return None


def format_sender_display(
    forwarder: str, original_sender: Optional[Dict[str, str]] = None
) -> str:
    """
    Format sender information for display

    Args:
        forwarder: The person who forwarded the email (from Gmail headers)
        original_sender: Optional dict with original sender info

    Returns:
        Formatted sender string
    """
    if not original_sender:
        return f"{forwarder} (forwarded)"

    # Show both forwarder and original sender
    original = f"{original_sender['name']} <{original_sender['email']}>"
    return f"{original} | Forwarded by: {forwarder}"


def is_trusted_forwarder(forwarder_email: str, trusted_forwarders: list) -> bool:
    """
    Check if forwarder is in trusted list

    Args:
        forwarder_email: Email address of forwarder
        trusted_forwarders: List of trusted forwarder emails

    Returns:
        True if trusted, False otherwise
    """
    return forwarder_email.lower() in [email.lower() for email in trusted_forwarders]
