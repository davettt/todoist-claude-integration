"""
Gmail API client for email processing operations
Follows OAuth2 pattern from google_calendar_client.py
"""

import base64
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class GmailClient:
    """Gmail API client with read and modify operations"""

    def __init__(self):
        self.service_name = "Gmail"
        self.gmail_service = None
        self._initialize_gmail_service()

    def _initialize_gmail_service(self):
        """Initialize Gmail service with OAuth2 authentication"""
        try:
            # Import Google API libraries
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            # Gmail API scopes
            # Using full gmail scope to enable read, modify, and delete operations
            SCOPES = ["https://mail.google.com/"]

            creds = None
            token_path = "local_data/gmail_token.json"
            credentials_path = "local_data/gmail_credentials.json"

            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        raise ValueError(
                            f"Gmail credentials not found at {credentials_path}\n"
                            "Please download credentials from Google Cloud Console and save as gmail_credentials.json\n"
                            "Note: Can use same credentials as calendar (calendar_credentials.json) if in same project"
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(token_path, "w") as token:
                    token.write(creds.to_json())

            self.gmail_service = build("gmail", "v1", credentials=creds)

        except ImportError:
            raise ValueError(
                "Gmail API libraries not installed.\n"
                "Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Gmail service: {str(e)}")

    def log_operation(self, operation: str, details: str = ""):
        """Log API operations with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {self.service_name}: {operation}"
        if details:
            log_message += f" - {details}"
        print(f"📝 {log_message}")

    def get_unread_messages(
        self, max_results: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch unread messages from Gmail inbox

        Args:
            max_results: Maximum number of messages to fetch

        Returns:
            List of message metadata (id, threadId) or None if error
        """
        try:
            results = (
                self.gmail_service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            self.log_operation("Fetched unread messages", f"{len(messages)} messages")
            return messages

        except Exception as e:
            print(f"❌ Error fetching unread messages: {str(e)}")
            return None

    def get_message_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full message details including headers and body

        Args:
            message_id: Gmail message ID

        Returns:
            Message details dict with headers and body, or None if error
        """
        try:
            message = (
                self.gmail_service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )

            # Extract headers
            headers = {}
            for header in message["payload"].get("headers", []):
                headers[header["name"].lower()] = header["value"]

            # Extract body
            body = self._extract_body(message["payload"])

            result = {
                "id": message["id"],
                "thread_id": message["threadId"],
                "headers": headers,
                "body": body,
                "snippet": message.get("snippet", ""),
                "internal_date": message.get("internalDate", ""),
            }

            self.log_operation("Fetched message details", f"ID: {message_id[:10]}...")
            return result

        except Exception as e:
            print(f"❌ Error fetching message {message_id}: {str(e)}")
            return None

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract email body from message payload (handles multipart and simple messages)

        Args:
            payload: Message payload from Gmail API

        Returns:
            Decoded email body text
        """
        body = ""

        # Check if multipart
        if "parts" in payload:
            for part in payload["parts"]:
                # Recursively extract from parts
                if part.get("mimeType") == "text/plain":
                    if "data" in part.get("body", {}):
                        body += self._decode_body(part["body"]["data"])
                elif part.get("mimeType") == "text/html" and not body:
                    # Use HTML only if no plain text found
                    if "data" in part.get("body", {}):
                        body += self._decode_body(part["body"]["data"])
                elif "parts" in part:
                    # Nested multipart
                    body += self._extract_body(part)
        else:
            # Simple message
            if "data" in payload.get("body", {}):
                body = self._decode_body(payload["body"]["data"])

        return body

    def _decode_body(self, data: str) -> str:
        """
        Decode base64url encoded message body

        Args:
            data: Base64url encoded string

        Returns:
            Decoded UTF-8 string
        """
        try:
            # Gmail uses base64url encoding
            decoded_bytes = base64.urlsafe_b64decode(data)

            # Try UTF-8 first, then fall back to other encodings
            for encoding in ["utf-8", "iso-8859-1", "ascii"]:
                try:
                    return decoded_bytes.decode(encoding)
                except UnicodeDecodeError:
                    continue

            # Last resort: decode with errors='ignore'
            return decoded_bytes.decode("utf-8", errors="ignore")

        except Exception as e:
            print(f"⚠️ Error decoding message body: {str(e)}")
            return ""

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.gmail_service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()

            self.log_operation("Marked as read", f"ID: {message_id[:10]}...")
            return True

        except Exception as e:
            print(f"❌ Error marking message as read: {str(e)}")
            return False

    def archive_message(self, message_id: str) -> bool:
        """
        Archive a message (mark as read + remove from inbox)

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.gmail_service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD", "INBOX"]}
            ).execute()

            self.log_operation("Archived message", f"ID: {message_id[:10]}...")
            return True

        except Exception as e:
            print(f"❌ Error archiving message: {str(e)}")
            return False

    def trash_message(self, message_id: str) -> bool:
        """
        Move message to trash (30-day auto-delete)

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.gmail_service.users().messages().trash(
                userId="me", id=message_id
            ).execute()

            self.log_operation("Trashed message", f"ID: {message_id[:10]}...")
            return True

        except Exception as e:
            print(f"❌ Error trashing message: {str(e)}")
            return False

    def delete_message(self, message_id: str) -> bool:
        """
        Delete a message permanently (bypasses trash)
        Use trash_message() instead for 30-day failsafe

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.gmail_service.users().messages().delete(
                userId="me", id=message_id
            ).execute()

            self.log_operation(
                "Permanently deleted message", f"ID: {message_id[:10]}..."
            )
            return True

        except Exception as e:
            print(f"❌ Error deleting message: {str(e)}")
            return False

    def extract_sender_info(self, from_header: str) -> Dict[str, str]:
        """
        Parse sender information from From header

        Args:
            from_header: Email From header (e.g., "John Doe <john@example.com>")

        Returns:
            Dict with 'name' and 'email' keys
        """
        import re

        # Pattern: "Name" <email> or Name <email> or just email
        match = re.match(r'^"?([^"<]+)"?\s*<([^>]+)>$', from_header.strip())

        if match:
            return {"name": match.group(1).strip(), "email": match.group(2).strip()}
        else:
            # Just an email address
            email = from_header.strip()
            return {
                "name": email.split("@")[0],  # Use part before @ as name
                "email": email,
            }
