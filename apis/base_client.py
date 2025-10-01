"""
Base API client for shared authentication and error handling patterns
Foundation for Todoist, Calendar, and Email API clients
"""

import requests
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BaseAPIClient:
    """Base class for all API clients with shared functionality"""
    
    def __init__(self, service_name: str, token_env_var: str):
        """
        Initialize base API client with secure token handling

        Args:
            service_name: Human-readable service name (e.g., "Todoist")
            token_env_var: Environment variable name for API token
        """
        self.service_name = service_name
        self.token_env_var = token_env_var
        self.api_token = os.getenv(token_env_var)

        # Validate token exists
        if not self.api_token:
            raise ValueError(
                f"❌ Error: {token_env_var} not found!\n"
                f"Please add your {service_name} API token to the .env file."
            )

        # Validate token format (basic sanity check)
        if len(self.api_token) < 20:
            raise ValueError(
                f"❌ Error: {token_env_var} appears to be invalid!\n"
                f"Token is too short (expected at least 20 characters).\n"
                f"Please check your {service_name} API token in the .env file."
            )

        # Check for common placeholder values
        placeholder_values = ['your_token_here', 'your_api_token', 'placeholder', 'xxxxx', 'your_todoist_api_token_here']
        if self.api_token.lower() in placeholder_values:
            raise ValueError(
                f"❌ Error: {token_env_var} contains a placeholder value!\n"
                f"Please replace it with your actual {service_name} API token in the .env file."
            )

        # Create masked version for safe logging (show first 4 and last 4 chars)
        if len(self.api_token) >= 8:
            self._masked_token = f"{self.api_token[:4]}...{self.api_token[-4:]}"
        else:
            self._masked_token = "****"
    
    def get_headers(self, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
        """Get standard headers for API requests"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def handle_response(self, response: requests.Response, operation: str = "operation") -> Optional[Dict[Any, Any]]:
        """
        Standardized response handling with error management
        
        Args:
            response: requests.Response object
            operation: Description of the operation for error messages
            
        Returns:
            JSON response data if successful, None if failed
        """
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            # No content (successful deletion, etc.)
            return {"success": True}
        elif response.status_code == 401:
            print(f"❌ Authentication failed for {self.service_name}")
            print(f"Please check your {self.token_env_var} in the .env file")
            return None
        elif response.status_code == 403:
            print(f"❌ Access forbidden for {operation}")
            print(f"Please check your {self.service_name} permissions")
            return None
        elif response.status_code == 404:
            print(f"❌ Resource not found for {operation}")
            return None
        elif response.status_code == 429:
            print(f"❌ Rate limit exceeded for {self.service_name}")
            print("Please wait a moment before trying again")
            return None
        else:
            print(f"❌ Failed {operation}: {response.status_code}")
            try:
                error_data = response.json()
                if isinstance(error_data, dict) and 'error' in error_data:
                    safe_error = self._sanitize_for_logging(str(error_data['error']))
                    print(f"Error details: {safe_error}")
                else:
                    safe_error = self._sanitize_for_logging(str(error_data))
                    print(f"Error details: {safe_error}")
            except:
                safe_text = self._sanitize_for_logging(response.text[:200])
                print(f"Error details: {safe_text}")
            return None
    
    def safe_request(self, method: str, url: str, operation: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """
        Make a safe API request with error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: API endpoint URL
            operation: Description of operation for error messages
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response data if successful, None if failed
        """
        try:
            response = requests.request(method, url, **kwargs)
            return self.handle_response(response, operation)
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error: Unable to reach {self.service_name}")
            print("Please check your internet connection")
            return None
        except requests.exceptions.Timeout:
            print(f"❌ Timeout error: {self.service_name} request took too long")
            return None
        except requests.exceptions.RequestException as e:
            safe_error = self._sanitize_for_logging(str(e))
            print(f"❌ Request error: {safe_error}")
            return None
    
    def log_operation(self, operation: str, details: str = ""):
        """Log API operations with timestamp (token-safe)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {self.service_name}: {operation}"
        if details:
            # Ensure token doesn't leak in details
            safe_details = self._sanitize_for_logging(details)
            log_message += f" - {safe_details}"

        # Could extend this to write to log files if needed
        print(f"📝 {log_message}")

    def _sanitize_for_logging(self, text: str) -> str:
        """
        Remove sensitive data from text before logging

        Args:
            text: Text that may contain sensitive information

        Returns:
            Sanitized text safe for logging
        """
        if not isinstance(text, str):
            return str(text)

        # Replace the actual token with masked version if it appears in text
        sanitized = text.replace(self.api_token, self._masked_token)

        # Also check for common token patterns (just in case)
        import re
        # Match Bearer tokens, API keys with common prefixes
        sanitized = re.sub(r'Bearer\s+[A-Za-z0-9_\-]{20,}', f'Bearer {self._masked_token}', sanitized)
        sanitized = re.sub(r'(api[_-]?key|token)["\']?\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}',
                          f'\\1: {self._masked_token}', sanitized, flags=re.IGNORECASE)

        return sanitized

    def get_masked_token(self) -> str:
        """
        Get masked version of token for safe display in logs/debugging

        Returns:
            Masked token string (e.g., "abcd...xyz1")
        """
        return self._masked_token

    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate that required fields are present in data
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            True if all required fields present, False otherwise
        """
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        return True
    
    def batch_operation(self, items: list, operation_func, batch_size: int = 10):
        """
        Process items in batches to respect rate limits
        
        Args:
            items: List of items to process
            operation_func: Function to call for each item
            batch_size: Number of items to process at once
        """
        import time
        
        success_count = 0
        total_items = len(items)
        
        for i in range(0, total_items, batch_size):
            batch = items[i:i + batch_size]
            print(f"🔄 Processing batch {i//batch_size + 1} ({len(batch)} items)...")
            
            for item in batch:
                if operation_func(item):
                    success_count += 1
                
                # Small delay to be respectful to API
                time.sleep(0.1)
            
            # Longer delay between batches
            if i + batch_size < total_items:
                time.sleep(1)
        
        print(f"✅ Completed: {success_count}/{total_items} operations successful")
        return success_count