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
            error_str = str(e)
            # Detect expired or revoked token
            if (
                "invalid_grant" in error_str
                or "Token has been expired or revoked" in error_str
            ):
                raise ValueError(
                    "EXPIRED_TOKEN: Your Gmail token has expired or been revoked.\n"
                    "Run: bash scripts/reauth_gmail.sh\n"
                    "Or manually delete local_data/gmail_token.json and try again."
                )
            raise ValueError(f"Failed to initialize Gmail service: {str(e)}")

    def _handle_api_error(
        self, error: Exception, operation: str = "Gmail API operation"
    ) -> bool:
        """
        Handle Gmail API errors with user-friendly messages.
        Detects token/auth issues and provides recovery instructions.
        """
        error_str = str(error)
        print(f"❌ Error during {operation}: {error_str}")

        # Detect token/authentication errors
        if (
            "failedPrecondition" in error_str
            or "Precondition check failed" in error_str
        ):
            print(
                "\n🔐 Authentication Error - Your Gmail token may be invalid or revoked."
            )
            print("Quick fix - run this command:")
            print("  bash scripts/reauth_gmail.sh")
            print(
                "\nNote: This only re-authenticates Gmail. Calendar uses a separate account/token."
            )
            return True  # Error was handled with user guidance
        return False  # Regular error, no special handling

    def log_operation(self, operation: str, details: str = ""):
        """Log API operations with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {self.service_name}: {operation}"
        if details:
            log_message += f" - {details}"
        print(f"📝 {log_message}")

    def get_unread_messages(
        self, max_results: int = 10, exclude_low_interest: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch unread messages from Gmail inbox

        Args:
            max_results: Maximum number of messages to fetch
            exclude_low_interest: If True, exclude emails labeled as low_interest (default: True)

        Returns:
            List of message metadata (id, threadId) or None if error
        """
        try:
            # Build query to exclude low_interest label
            query = None
            if exclude_low_interest:
                query = "-label:low_interest"

            results = (
                self.gmail_service.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=["INBOX", "UNREAD"],
                    maxResults=max_results,
                    q=query,
                )
                .execute()
            )

            messages = results.get("messages", [])
            exclusion_note = " (excluding low_interest)" if exclude_low_interest else ""
            self.log_operation(
                f"Fetched unread messages{exclusion_note}", f"{len(messages)} messages"
            )
            return messages

        except Exception as e:
            self._handle_api_error(e, "fetching unread messages")
            return None

    def get_recent_messages(
        self,
        max_results: int = 200,
        label_ids: Optional[List[str]] = None,
        exclude_low_interest: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch recent messages from Gmail inbox (both read and unread)

        Args:
            max_results: Maximum number of messages to fetch
            label_ids: List of label IDs to filter by (default: INBOX only)
            exclude_low_interest: If True, exclude emails labeled as low_interest (default: True)

        Returns:
            List of message metadata (id, threadId) or None if error
        """
        try:
            if label_ids is None:
                label_ids = ["INBOX"]

            # Build query to exclude low_interest label
            query = None
            if exclude_low_interest:
                query = "-label:low_interest"

            results = (
                self.gmail_service.users()
                .messages()
                .list(userId="me", labelIds=label_ids, maxResults=max_results, q=query)
                .execute()
            )

            messages = results.get("messages", [])
            exclusion_note = " (excluding low_interest)" if exclude_low_interest else ""
            self.log_operation(
                f"Fetched recent messages{exclusion_note}", f"{len(messages)} messages"
            )
            return messages

        except Exception as e:
            self._handle_api_error(e, "fetching recent messages")
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
            self._handle_api_error(e, f"fetching message {message_id}")
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
            self._handle_api_error(e, "marking message as read")
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
            self._handle_api_error(e, "archiving message")
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
            self._handle_api_error(e, "trashing message")
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
            self._handle_api_error(e, "deleting message")
            return False

    def get_or_create_label(self, label_name: str) -> Optional[str]:
        """
        Get or create a Gmail label by name

        Args:
            label_name: Name of the label to get or create

        Returns:
            Label ID if successful, None otherwise
        """
        try:
            # Get all labels
            results = self.gmail_service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            # Check if label already exists
            for label in labels:
                if label["name"] == label_name:
                    self.log_operation(
                        f"Found existing label '{label_name}'", f"ID: {label['id']}"
                    )
                    return label["id"]

            # Label doesn't exist, create it
            label_object = {
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            }

            created_label = (
                self.gmail_service.users()
                .labels()
                .create(userId="me", body=label_object)
                .execute()
            )

            self.log_operation(
                f"Created new label '{label_name}'", f"ID: {created_label['id']}"
            )
            return created_label["id"]

        except Exception as e:
            self._handle_api_error(e, f"getting or creating label '{label_name}'")
            return None

    def add_label_to_message(self, message_id: str, label_name: str) -> bool:
        """
        Add a label to a message (creates label if it doesn't exist)

        Args:
            message_id: Gmail message ID
            label_name: Name of the label to add

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get or create label
            label_id = self.get_or_create_label(label_name)
            if not label_id:
                return False

            # Add label to message
            self.gmail_service.users().messages().modify(
                userId="me", id=message_id, body={"addLabelIds": [label_id]}
            ).execute()

            self.log_operation(
                f"Added label '{label_name}'", f"ID: {message_id[:10]}..."
            )
            return True

        except Exception as e:
            self._handle_api_error(e, f"adding label '{label_name}' to message")
            return False

    def mark_as_read_and_label_low_interest(self, message_id: str) -> bool:
        """
        Mark message as read and add 'low_interest' label
        This is used for automatically handling LOW-rated emails from AI analysis

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get or create low_interest label
            label_id = self.get_or_create_label("low_interest")
            if not label_id:
                return False

            # Mark as read AND add label in single operation
            self.gmail_service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"], "addLabelIds": [label_id]},
            ).execute()

            self.log_operation(
                "Marked as read + low_interest", f"ID: {message_id[:10]}..."
            )
            return True

        except Exception as e:
            self._handle_api_error(e, "marking message as read and low_interest")
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
