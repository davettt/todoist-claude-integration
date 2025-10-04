"""
Claude API Client
Handles communication with Anthropic's Claude API for email analysis
"""

import json
import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class ClaudeAPIClient:
    """Client for interacting with Claude API"""

    def __init__(self):
        """Initialize Claude API client with API key from environment"""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "❌ ANTHROPIC_API_KEY not found!\n"
                "Please add your Anthropic API key to the .env file.\n"
                "Get your API key from: https://console.anthropic.com/"
            )

        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.max_tokens = int(os.getenv("CLAUDE_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("CLAUDE_TEMPERATURE", "0.3"))

    def analyze_email_interest(
        self,
        email_content: str,
        email_subject: str,
        email_from: str,
        user_profile: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze email for interest level and extract key points

        Args:
            email_content: Sanitized email body
            email_subject: Email subject line
            email_from: Sender information
            user_profile: User's interest profile

        Returns:
            Dict with level, category, bullets, reasoning, confidence
            None if API call fails
        """
        try:
            prompt = self._build_interest_analysis_prompt(
                email_content, email_subject, email_from, user_profile
            )

            response = self._call_claude_api(prompt)

            if response:
                return self._parse_interest_analysis(response)

            return None

        except Exception as e:
            print(f"❌ Error analyzing email: {str(e)}")
            return None

    def _build_interest_analysis_prompt(
        self,
        email_content: str,
        email_subject: str,
        email_from: str,
        user_profile: Dict[str, Any],
    ) -> str:
        """Build prompt for interest analysis"""

        # Extract user context
        core_interests = user_profile.get("core_interests", [])
        active_projects = user_profile.get("active_projects", [])
        trusted_senders = user_profile.get("trusted_senders", [])
        trusted_forwarders = user_profile.get("trusted_forwarders", [])
        urgency_keywords = user_profile.get("urgency_keywords", [])
        auto_skip_keywords = user_profile.get("auto_skip_keywords", [])
        is_trusted_sender = user_profile.get("current_sender_is_trusted", False)
        is_from_user = user_profile.get("forwarded_by_user", True)

        sender_trust = "✓ TRUSTED SENDER" if is_trusted_sender else "⚠ Unknown sender"
        forwarder_trust = (
            "✓ Forwarded by user"
            if is_from_user
            else "⚠️ NOT from user's accounts (suspicious!)"
        )

        prompt = f"""You are analyzing an email to determine if the user would find it interesting and worth reading.

USER PROFILE:
- Core interests: {', '.join(core_interests)}
- Active projects: {', '.join(active_projects)}
- User's email addresses: {', '.join(trusted_forwarders[:3])}
- Trusted email senders: {', '.join(trusted_senders[:5])}
- Urgency keywords: {', '.join(urgency_keywords)}
- Auto-skip keywords: {', '.join(auto_skip_keywords)}

SECURITY STATUS:
- Email forwarder: {forwarder_trust}
- Original sender: {sender_trust}

EMAIL TO ANALYZE:
From: {email_from}
Subject: {email_subject}

Content (URLs/emails removed for security):
{email_content[:2000]}

TASK:
Analyze this email and provide a structured assessment.

INTEREST LEVELS:
- "urgent": Security alerts, payment issues, account problems (requires immediate action)
- "high": Directly matches core interests, from trusted senders, actionable content
- "medium": Somewhat interesting, may be useful, worth skimming (untrusted senders rarely deserve high rating)
- "low": Generic content, promotional, doesn't match interests

SENDER TRUST IMPACT:
- Trusted senders: Content from trusted sources should be rated higher (high vs medium)
- Unknown senders: Even relevant content should rarely exceed medium rating unless exceptional
- This helps prioritize reliable sources over random newsletters

CATEGORIES:
- "security": Security alerts, suspicious activity
- "account": Payment issues, subscription problems, account changes
- "trusted_content": From trusted senders (newsletters, blogs)
- "promotional": Sales, discounts, marketing
- "informational": News, updates, announcements
- "other": Doesn't fit above categories

OUTPUT FORMAT (JSON only, no markdown):
{{
  "level": "urgent|high|medium|low",
  "category": "security|account|trusted_content|promotional|informational|other",
  "bullets": [
    {{
      "content": "Key point from email (specific, actionable)",
      "reasoning": "Why this matters to the user"
    }}
  ],
  "overall_reasoning": "Explain why you chose this interest level, considering user's profile",
  "confidence": "high|medium|low"
}}

IMPORTANT:
- Be specific in bullets (quotes, facts, actionable items, concrete details)
- For urgent/high: Extract 2-3 most important points with actionable context
- For medium: Extract 2-3 key points with SPECIFIC details (what exactly is offered, specific topics covered, concrete takeaways) so user can decide if worth reading
- For low: Extract 1-2 specific points explaining exactly what the email contains and why it's skippable
- Include specific examples, topics, or quotes from the email - don't be vague
- If there are action items (links to click, things to do), mention them specifically
- Consider user's specific interests and projects
- Urgency beats interest (security alert is urgent even if not interesting)

Respond ONLY with valid JSON. No backticks, no markdown, ONLY JSON."""

        return prompt

    def _call_claude_api(self, prompt: str) -> Optional[str]:
        """
        Make API call to Claude

        Args:
            prompt: The prompt to send

        Returns:
            API response text or None if failed
        """
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            data = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            response = requests.post(
                self.api_url, headers=headers, json=data, timeout=30
            )

            if response.status_code == 200:
                response_data = response.json()
                content = response_data["content"][0]["text"]
                return content
            elif response.status_code == 429:
                print("⚠️  Rate limit exceeded. Please wait before retrying.")
                return None
            elif response.status_code == 401:
                print("❌ Authentication failed. Check your ANTHROPIC_API_KEY.")
                return None
            else:
                print(f"❌ API error: {response.status_code}")
                print(f"   {response.text[:200]}")
                return None

        except requests.exceptions.Timeout:
            print("❌ API request timed out")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Connection error. Check your internet connection.")
            return None
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            return None

    def _parse_interest_analysis(self, api_response: str) -> Optional[Dict[str, Any]]:
        """
        Parse Claude's response into structured data

        Args:
            api_response: Raw API response text

        Returns:
            Parsed analysis dict or None if parsing fails
        """
        try:
            # Claude should return pure JSON, but handle markdown fences just in case
            response_text = api_response.strip()

            # Remove markdown code fences if present
            if response_text.startswith("```"):
                # Find the first newline and last ```
                lines = response_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]  # Remove first ```json or ```
                if lines[-1].strip() == "```":
                    lines = lines[:-1]  # Remove last ```
                response_text = "\n".join(lines)

            # Parse JSON
            analysis = json.loads(response_text)

            # Validate required fields
            required_fields = ["level", "category", "bullets", "overall_reasoning"]
            for field in required_fields:
                if field not in analysis:
                    print(f"⚠️  Missing field in analysis: {field}")
                    return None

            # Validate interest level
            valid_levels = ["urgent", "high", "medium", "low"]
            if analysis["level"] not in valid_levels:
                print(f"⚠️  Invalid interest level: {analysis['level']}")
                analysis["level"] = "medium"  # Default fallback

            # Ensure bullets is a list
            if not isinstance(analysis["bullets"], list):
                analysis["bullets"] = []

            return analysis

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse API response as JSON: {str(e)}")
            print(f"   Response: {api_response[:200]}...")
            return None
        except Exception as e:
            print(f"❌ Error parsing analysis: {str(e)}")
            return None

    def estimate_cost(self, email_count: int) -> Dict[str, Any]:
        """
        Estimate API cost for processing emails

        Args:
            email_count: Number of emails to process

        Returns:
            Dict with token and cost estimates
        """
        # Rough estimates based on typical email analysis
        avg_input_tokens_per_email = 800  # prompt + email content
        avg_output_tokens_per_email = 300  # analysis JSON

        total_input_tokens = email_count * avg_input_tokens_per_email
        total_output_tokens = email_count * avg_output_tokens_per_email

        # Claude Sonnet 4 pricing (as of 2024)
        input_cost_per_1k = 0.003
        output_cost_per_1k = 0.015

        input_cost = (total_input_tokens / 1000) * input_cost_per_1k
        output_cost = (total_output_tokens / 1000) * output_cost_per_1k
        total_cost = input_cost + output_cost

        return {
            "email_count": email_count,
            "estimated_input_tokens": total_input_tokens,
            "estimated_output_tokens": total_output_tokens,
            "estimated_input_cost": input_cost,
            "estimated_output_cost": output_cost,
            "estimated_total_cost": total_cost,
        }

    def test_connection(self) -> bool:
        """
        Test API connection and key validity

        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_prompt = "Respond with just the word 'success' if you can read this."

            response = self._call_claude_api(test_prompt)

            if response:
                print("✅ Claude API connection successful")
                print(f"   Model: {self.model}")
                return True
            else:
                print("❌ Claude API connection failed")
                return False

        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False
