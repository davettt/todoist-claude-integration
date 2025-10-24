"""
Adaptive AI Context Generator
Generates dynamic AI prompts based on user learning preferences
"""

import json
import os
from typing import Any, Dict


class AdaptiveAIContext:
    """Generates adaptive context for AI analysis based on learning"""

    def __init__(
        self,
        profile_path: str = "local_data/personal_data/email_interest_profile.json",
    ):
        """Initialize adaptive context generator"""
        self.profile_path = profile_path
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        """Load user profile"""
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def generate_analysis_prompt(
        self,
        base_prompt: str,
        learning_context: Dict[str, Any],
        email_from: str = "",
    ) -> str:
        """
        Generate adaptive prompt for email analysis

        Args:
            base_prompt: Base analysis prompt
            learning_context: Learning insights from feedback
            email_from: Email sender (for sender-specific adjustments)

        Returns:
            Modified prompt incorporating learned preferences
        """
        prompt = base_prompt

        if (
            not learning_context
            or learning_context.get("status") == "insufficient_data"
        ):
            return prompt

        # Add learned preferences section
        preferences_section = (
            "\n\n## User's Learned Preferences (from feedback analysis):"
        )

        # Add strongest areas emphasis
        strongest = learning_context.get("learned_preferences", {}).get(
            "strongest_areas", []
        )
        if strongest:
            preferences_section += f"\n- **Strong matches for:** {', '.join(strongest.title() for strongest in strongest)}"
            preferences_section += (
                "\n  → Be more generous with interest ratings for these topics"
            )

        # Add weakest areas note
        weakest = learning_context.get("learned_preferences", {}).get(
            "weakest_areas", []
        )
        if weakest:
            preferences_section += f"\n- **Previous misses with:** {', '.join(weakest.title() for weakest in weakest)}"
            preferences_section += "\n  → Extra scrutiny recommended for these topics"

        # Add sender-specific preferences
        trusted_senders = self.profile.get("trusted_senders", [])
        if trusted_senders and email_from:
            is_trusted = any(ts.lower() in email_from.lower() for ts in trusted_senders)
            if is_trusted:
                preferences_section += "\n- **Sender is on trusted list**"
                preferences_section += "\n  → Increase interest rating slightly for content from this sender"

        # Add confidence threshold note
        weights = learning_context.get("weights", {})
        if weights:
            base_confidence = weights.get("base_confidence", 0.7)
            if base_confidence >= 0.75:
                preferences_section += "\n- **Historical accuracy is high**"
                preferences_section += (
                    "\n  → Maintain consistent prediction methodology"
                )
            elif base_confidence < 0.6:
                preferences_section += "\n- **Historical accuracy is lower than ideal**"
                preferences_section += (
                    "\n  → Consider asking for clarification in reasoning"
                )

        return prompt + preferences_section

    def generate_learnings_summary_for_prompt(
        self, learning_context: Dict[str, Any]
    ) -> str:
        """
        Generate a brief summary of learning for inclusion in prompts

        Args:
            learning_context: Learning context from engine

        Returns:
            Brief summary text suitable for prompts
        """
        if (
            not learning_context
            or learning_context.get("status") == "insufficient_data"
        ):
            return "Not enough feedback data yet for learning adjustments."

        summary_lines = []

        # Accuracy trend
        weights = learning_context.get("weights", {})
        base_conf = weights.get("base_confidence", 0)

        if base_conf >= 0.8:
            summary_lines.append(
                f"✓ Strong prediction track record ({base_conf*100:.0f}% confidence)"
            )
        elif base_conf >= 0.6:
            summary_lines.append(
                f"→ Moderate accuracy ({base_conf*100:.0f}% confidence)"
            )
        else:
            summary_lines.append(f"⚠ Learning phase ({base_conf*100:.0f}% confidence)")

        # Strong areas
        strongest = learning_context.get("learned_preferences", {}).get(
            "strongest_areas", []
        )
        if strongest:
            summary_lines.append(f"✓ Excellent with: {', '.join(strongest[:2])}")

        # Weak areas
        weakest = learning_context.get("learned_preferences", {}).get(
            "weakest_areas", []
        )
        if weakest:
            summary_lines.append(f"⚠ Challenge with: {', '.join(weakest[:2])}")

        return " | ".join(summary_lines)

    def get_confidence_override(
        self, learning_context: Dict[str, Any], base_level: str
    ) -> str:
        """
        Get potentially adjusted confidence level based on learning

        Args:
            learning_context: Learning context
            base_level: Original predicted level (urgent/high/medium/low)

        Returns:
            Potentially adjusted level
        """
        if (
            not learning_context
            or learning_context.get("status") == "insufficient_data"
        ):
            return base_level

        weights = learning_context.get("weights", {})
        level_key = f"level_{base_level}_confidence"

        if level_key in weights:
            confidence = weights[level_key]

            # Very low confidence in this level → consider adjusting
            if confidence < 0.5 and base_level != "urgent":
                # Suggest downgrade
                return f"{base_level}*"  # Mark as uncertain

        return base_level

    def get_analysis_notes(self, learning_context: Dict[str, Any]) -> str:
        """
        Get notes about what the system has learned

        Args:
            learning_context: Learning context from engine

        Returns:
            Human-readable notes about learning
        """
        if (
            not learning_context
            or learning_context.get("status") == "insufficient_data"
        ):
            return "System is still learning from your feedback. Start rating emails to see personalization."

        notes = []

        weights = learning_context.get("weights", {})
        base_conf = weights.get("base_confidence", 0)

        if base_conf > 0.8:
            notes.append(
                f"📈 System has strong understanding of your preferences ({base_conf*100:.0f}% accuracy)"
            )
        elif base_conf > 0.6:
            notes.append(f"📊 System is learning ({base_conf*100:.0f}% accuracy so far)")
        else:
            notes.append(
                f"🆕 System is in early learning phase ({base_conf*100:.0f}% accuracy)"
            )

        # Learning adjustments applied
        adjustments = learning_context.get("learning_adjustments", {})
        if adjustments.get("use_learned_sender_preferences"):
            notes.append("✓ Using learned sender preferences")
        if adjustments.get("emphasize_strongest_areas"):
            notes.append("✓ Emphasizing your strongest areas")
        if adjustments.get("apply_confidence_adjustments"):
            notes.append("✓ Applying confidence-based adjustments")

        return (
            " | ".join(notes)
            if notes
            else "Standard analysis (learning not yet activated)"
        )
