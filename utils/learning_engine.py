"""
AI Learning Engine
Analyzes user feedback patterns to improve email digest predictions
Generates profile suggestions and adaptive AI prompting context
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional


class LearningEngine:
    """Analyzes feedback patterns and generates learning insights"""

    def __init__(
        self,
        feedback_log_path: str = "local_data/personal_data/email_feedback_log.json",
        profile_path: str = "local_data/personal_data/email_interest_profile.json",
    ):
        """Initialize learning engine"""
        self.feedback_log_path = feedback_log_path
        self.profile_path = profile_path
        self.feedback_data = self._load_feedback_log()
        self.profile = self._load_profile()

    def _load_feedback_log(self) -> Dict[str, Any]:
        """Load feedback log"""
        if os.path.exists(self.feedback_log_path):
            try:
                with open(self.feedback_log_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {"feedback_entries": []}
        return {"feedback_entries": []}

    def _load_profile(self) -> Dict[str, Any]:
        """Load user profile"""
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """
        Analyze user feedback patterns to identify trends and biases

        Returns:
            Dict with detailed analysis of feedback patterns
        """
        entries = self.feedback_data.get("feedback_entries", [])

        if len(entries) < 5:
            return {
                "status": "insufficient_data",
                "message": f"Need at least 5 feedback entries (have {len(entries)})",
                "feedback_count": len(entries),
            }

        analysis = {
            "feedback_count": len(entries),
            "accuracy_by_level": self._analyze_accuracy_by_level(entries),
            "sender_patterns": self._analyze_sender_patterns(entries),
            "time_trends": self._analyze_time_trends(entries),
            "feedback_type_distribution": self._analyze_feedback_distribution(entries),
            "strongest_areas": self._identify_strongest_areas(entries),
            "weakest_areas": self._identify_weakest_areas(entries),
        }

        return analysis

    def _analyze_accuracy_by_level(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze prediction accuracy by interest level"""
        by_level = defaultdict(lambda: {"total": 0, "accurate": 0})

        for entry in entries:
            level = entry.get("predicted_level", "unknown")
            by_level[level]["total"] += 1
            if entry.get("was_accurate", False):
                by_level[level]["accurate"] += 1

        result = {}
        for level, stats in by_level.items():
            if stats["total"] > 0:
                accuracy = (stats["accurate"] / stats["total"]) * 100
                result[level] = {
                    "total": stats["total"],
                    "accurate": stats["accurate"],
                    "accuracy": round(accuracy, 1),
                }

        return result

    def _analyze_sender_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze patterns by sender with correct priority interpretation"""
        by_sender = defaultdict(
            lambda: {
                "total": 0,
                "high_value": 0,
                "escalated": 0,
                "agreed_low": 0,
                "accurate": 0,
            }
        )

        for entry in entries:
            sender = entry.get("email_from", "Unknown")
            predicted_level = entry.get("predicted_level", "").lower()
            actual_interest = entry.get("actual_interest", "")

            by_sender[sender]["total"] += 1

            # Track high-value interactions (escalations or high/urgent agreements)
            if actual_interest == "more_important":
                by_sender[sender]["escalated"] += 1
                by_sender[sender]["high_value"] += 1
            elif actual_interest == "useful" and predicted_level in ["high", "urgent"]:
                by_sender[sender]["high_value"] += 1
            elif actual_interest == "useful" and predicted_level in ["medium", "low"]:
                # Track low-priority agreements for context
                by_sender[sender]["agreed_low"] += 1

            if entry.get("was_accurate", False):
                by_sender[sender]["accurate"] += 1

        # Calculate meaningful metrics and filter
        result = {}
        for sender, stats in by_sender.items():
            if stats["total"] >= 3:  # Only include senders with 3+ emails
                high_value_rate = (
                    stats["high_value"] / stats["total"] * 100
                    if stats["total"] > 0
                    else 0
                )
                escalation_rate = (
                    stats["escalated"] / stats["total"] * 100
                    if stats["total"] > 0
                    else 0
                )
                accuracy = (stats["accurate"] / stats["total"]) * 100

                result[sender] = {
                    "total_emails": stats["total"],
                    "high_value_emails": stats["high_value"],
                    "high_value_rate": round(high_value_rate, 1),
                    "escalated_emails": stats["escalated"],
                    "escalation_rate": round(escalation_rate, 1),
                    "accuracy": round(accuracy, 1),
                }

        # Sort by total emails
        return dict(
            sorted(result.items(), key=lambda x: x[1]["total_emails"], reverse=True)
        )

    def _analyze_time_trends(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how accuracy trends over time"""
        if len(entries) < 10:
            return {"status": "insufficient_data", "message": "Need 10+ entries"}

        # Split into early and recent
        early = entries[: len(entries) // 2]
        recent = entries[len(entries) // 2 :]

        early_accuracy = (
            sum(1 for e in early if e.get("was_accurate")) / len(early) * 100
            if early
            else 0
        )
        recent_accuracy = (
            sum(1 for e in recent if e.get("was_accurate")) / len(recent) * 100
            if recent
            else 0
        )

        trend = (
            "improving"
            if recent_accuracy > early_accuracy * 1.05
            else "declining"
            if recent_accuracy < early_accuracy * 0.95
            else "stable"
        )

        return {
            "early_accuracy": round(early_accuracy, 1),
            "recent_accuracy": round(recent_accuracy, 1),
            "trend": trend,
            "improvement": round(recent_accuracy - early_accuracy, 1),
        }

    def _analyze_feedback_distribution(self, entries: List[Dict[str, Any]]) -> Dict:
        """Analyze distribution of feedback types"""
        distribution = Counter(e.get("feedback_type", "unknown") for e in entries)
        return dict(distribution)

    def _identify_strongest_areas(self, entries: List[Dict[str, Any]]) -> List[str]:
        """Identify topics/senders where accuracy is highest"""
        by_level = self._analyze_accuracy_by_level(entries)
        strong = [
            level for level, stats in by_level.items() if stats.get("accuracy", 0) >= 80
        ]
        return strong

    def _identify_weakest_areas(self, entries: List[Dict[str, Any]]) -> List[str]:
        """Identify topics/senders where accuracy is lowest"""
        by_level = self._analyze_accuracy_by_level(entries)
        weak = [
            level for level, stats in by_level.items() if stats.get("accuracy", 0) < 60
        ]
        return weak

    def generate_profile_suggestions(self) -> Dict[str, Any]:
        """
        Generate suggestions for profile updates based on feedback patterns

        Returns:
            Dict with suggestions for interests, projects, and senders
        """
        entries = self.feedback_data.get("feedback_entries", [])

        if len(entries) < 10:
            return {
                "status": "insufficient_data",
                "message": "Need at least 10 feedback entries for suggestions",
                "current_feedback_count": len(entries),
            }

        suggestions = {
            "add_interests": self._suggest_interests_to_add(entries),
            "remove_interests": self._suggest_interests_to_remove(entries),
            "add_senders": self._suggest_senders_to_add(entries),
            "confidence_notes": self._generate_confidence_notes(entries),
        }

        return suggestions

    def _suggest_interests_to_add(self, entries: List[Dict[str, Any]]) -> List[Dict]:
        """Suggest interests based on AI-analyzed high-value content patterns"""
        # Analyze last 100 entries for better pattern detection (previously was 30)
        high_value_entries = self._get_high_value_entries(entries[-100:])

        if not high_value_entries:
            return []

        current_interests = set(self.profile.get("core_interests", []))
        suggestions = []
        tech_scores = Counter()
        topic_scores = Counter()

        # Analyze AI-identified patterns in high-value content
        for entry in high_value_entries:
            ai_analysis = entry.get("ai_analysis", {})

            # Extract technologies mentioned
            technologies = ai_analysis.get("technologies_mentioned", [])
            for tech in technologies:
                tech_scores[tech] += 1

            # If no explicit technologies but we have reasoning, try to extract from there
            if not technologies and ai_analysis.get("reasoning"):
                reasoning = ai_analysis.get("reasoning", "").lower()
                # Look for common tech terms in reasoning
                tech_keywords = [
                    "docker",
                    "kubernetes",
                    "python",
                    "javascript",
                    "github",
                    "ai",
                    "ml",
                    "machine learning",
                    "react",
                    "node",
                    "aws",
                    "azure",
                ]
                for tech in tech_keywords:
                    if tech in reasoning:
                        tech_scores[tech] += 1

            # Extract topics identified
            topics = ai_analysis.get("topics_identified", [])
            for topic in topics:
                topic_scores[topic] += 1

            # If no explicit topics but we have category, infer from it
            if not topics and ai_analysis.get("category"):
                category = ai_analysis.get("category", "").lower()
                if "developer" in category or "dev" in category:
                    topic_scores["developer tools"] += 1
                if "trusted" in category or "newsletter" in category:
                    topic_scores["trusted content"] += 1
                if "informational" in category or "news" in category:
                    topic_scores["technology news"] += 1

        # Determine threshold based on dataset size
        # For small datasets (< 15 entries), lower threshold to catch emerging interests
        # For larger datasets, use stricter threshold to avoid noise
        threshold = 1 if len(high_value_entries) < 15 else 2

        # Suggest technologies
        for tech, count in tech_scores.most_common(5):
            if count >= threshold and tech.title() not in current_interests:
                confidence = (
                    "High Confidence"
                    if count >= 2
                    else f"Emerging interest ({count} mention)"
                )
                suggestions.append(
                    {
                        "interest": tech.title(),
                        "confidence": confidence,
                        "reason": f"Mentioned in {count} escalated email(s) you rated highly",
                    }
                )

        # Suggest topics
        for topic, count in topic_scores.most_common(5):
            if count >= threshold and topic.title() not in current_interests:
                # Only add if not already suggested (avoid duplicates)
                if not any(s["interest"].lower() == topic.lower() for s in suggestions):
                    confidence = (
                        "High Confidence"
                        if count >= 2
                        else f"Emerging theme ({count} mention)"
                    )
                    suggestions.append(
                        {
                            "interest": topic.title(),
                            "confidence": confidence,
                            "reason": f"Consistent topic in {count} high-value email(s) you find valuable",
                        }
                    )

        # Fallback to keyword extraction if no AI analysis data
        if not suggestions:
            keyword_scores = Counter()
            for entry in high_value_entries:
                subject = entry.get("email_subject", "").lower()
                words = subject.split()
                for word in words:
                    if len(word) > 4 and word not in ["email", "message"]:
                        keyword_scores[word] += 1

            for keyword, score in keyword_scores.most_common(5):
                if (
                    keyword.title() not in current_interests
                    and score >= 2
                    and keyword.isalpha()
                ):
                    suggestions.append(
                        {
                            "interest": keyword.title(),
                            "confidence": f"{score} recent high-value emails",
                            "reason": "Found in escalated or high-priority content you rated highly",
                        }
                    )

        return suggestions[:5]  # Limit to top 5

    def _suggest_interests_to_remove(self, entries: List[Dict[str, Any]]) -> List[Dict]:
        """Suggest interests to remove based on low ratings"""
        low_rated = [
            e
            for e in entries[-30:]
            if e.get("actual_interest") in ["not_interesting", "less_important"]
        ]

        if not low_rated:
            return []

        # For now, suggest general advice rather than specific interests
        suggestions = []

        if len(low_rated) > len(entries[-30:]) * 0.4:
            suggestions.append(
                {
                    "interest": "Review current interests",
                    "confidence": f"{len(low_rated)}/{len(entries[-30:])} recent emails rated low",
                    "reason": "Many recent emails not matching interests",
                }
            )

        return suggestions

    def _suggest_senders_to_add(self, entries: List[Dict[str, Any]]) -> List[Dict]:
        """Suggest senders based on consistently high-value content (escalations or high-priority agreements)"""
        sender_stats = defaultdict(
            lambda: {"total": 0, "high_value": 0, "escalated": 0}
        )

        for entry in entries:
            sender = entry.get("email_from", "Unknown")
            predicted_level = entry.get("predicted_level", "").lower()
            actual_interest = entry.get("actual_interest", "")

            sender_stats[sender]["total"] += 1

            # High-value: user escalated (⬆️) OR agreed with high/urgent prediction
            # NOT: user agreed with low/medium prediction (that's just low-priority agreement)
            if actual_interest == "more_important":
                sender_stats[sender]["escalated"] += 1
                sender_stats[sender]["high_value"] += 1
            elif actual_interest == "useful" and predicted_level in ["high", "urgent"]:
                sender_stats[sender]["high_value"] += 1

        current_senders = set(self.profile.get("trusted_senders", []))
        suggestions = []

        for sender, stats in sender_stats.items():
            if stats["total"] >= 3:
                high_value_rate = (
                    stats["high_value"] / stats["total"] if stats["total"] > 0 else 0
                )
                escalation_rate = (
                    stats["escalated"] / stats["total"] if stats["total"] > 0 else 0
                )

                # Suggest if high_value_rate ≥30% OR escalation_rate ≥20%
                if (high_value_rate >= 0.3 or escalation_rate >= 0.2) and (
                    sender not in current_senders
                ):
                    suggestions.append(
                        {
                            "sender": sender,
                            "confidence": f"{stats['high_value']}/{stats['total']} high-value ({high_value_rate*100:.0f}%)",
                            "reason": f"Consistently escalated ({escalation_rate*100:.0f}%) or high-priority",
                        }
                    )

        return suggestions[:5]  # Limit to top 5

    def _generate_confidence_notes(self, entries: List[Dict[str, Any]]) -> str:
        """Generate notes about confidence in suggestions"""
        total = len(entries)
        if total < 20:
            return "Low confidence (few feedback entries). Provide more ratings."
        elif total < 50:
            return "Medium confidence. More feedback will improve suggestions."
        else:
            return "High confidence. Suggestions based on substantial feedback."

    def calculate_learning_weights(self) -> Dict[str, float]:
        """
        Calculate learning weights for adjusting AI analysis

        Returns:
            Dict with weight adjustments for different factors
        """
        entries = self.feedback_data.get("feedback_entries", [])

        if not entries:
            return {"status": "no_data"}

        # Calculate base accuracy
        overall_accuracy = (
            sum(1 for e in entries if e.get("was_accurate")) / len(entries) * 100
        )

        # Calculate weight adjustments
        weights = {
            "base_confidence": overall_accuracy / 100,
            "minimum_confidence_threshold": max(0.3, (overall_accuracy - 10) / 100),
            "trusted_sender_boost": 1.5 if overall_accuracy >= 70 else 1.2,
            "anti_patterns_weight": min(1.5, 2.0 - (overall_accuracy / 100)),
        }

        # Add per-level weights
        by_level = self._analyze_accuracy_by_level(entries)
        for level, stats in by_level.items():
            accuracy = stats.get("accuracy", 0)
            weights[f"level_{level}_confidence"] = accuracy / 100

        return weights

    def get_adaptive_context(self) -> Dict[str, Any]:
        """
        Generate context for adaptive AI prompting

        Returns:
            Dict with context for modifying AI prompts
        """
        analysis = self.analyze_feedback_patterns()

        if analysis.get("status") == "insufficient_data":
            return {"status": "insufficient_data", "message": analysis.get("message")}

        context = {
            "status": "ready",
            "learned_preferences": {
                "strongest_areas": analysis.get("strongest_areas", []),
                "weakest_areas": analysis.get("weakest_areas", []),
            },
            "learning_adjustments": {
                "use_learned_sender_preferences": len(
                    self._load_profile().get("trusted_senders", [])
                )
                > 0,
                "emphasize_strongest_areas": len(analysis.get("strongest_areas", []))
                > 0,
                "apply_confidence_adjustments": True,
            },
            "weights": self.calculate_learning_weights(),
        }

        return context

    def get_learning_summary(self) -> Dict[str, Any]:
        """Generate a summary of learning insights"""
        entries = self.feedback_data.get("feedback_entries", [])

        if not entries:
            return {"status": "no_feedback", "message": "No feedback data available"}

        analysis = self.analyze_feedback_patterns()
        suggestions = self.generate_profile_suggestions()

        summary = {
            "status": "active",
            "total_feedback_entries": len(entries),
            "accuracy_analysis": analysis,
            "profile_suggestions": suggestions,
            "learning_weights": self.calculate_learning_weights(),
        }

        return summary

    def analyze_content_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in AI-identified content from high-value emails

        Returns:
            Dict with category preferences, technology interests, and topic themes
        """
        entries = self.feedback_data.get("feedback_entries", [])
        high_value_entries = self._get_high_value_entries(entries)

        if not high_value_entries:
            return {"status": "insufficient_data", "message": "No high-value entries"}

        analysis = {
            "status": "active",
            "high_value_count": len(high_value_entries),
            "preferred_categories": self._analyze_category_preferences(
                high_value_entries
            ),
            "technology_interests": self._analyze_technology_mentions(
                high_value_entries
            ),
            "topic_themes": self._analyze_topic_patterns(high_value_entries),
        }

        return analysis

    def _get_high_value_entries(self, entries: List[Dict[str, Any]]) -> List[Dict]:
        """Filter entries to only those with high value (escalations or useful agreements)"""
        high_value = []
        for entry in entries:
            actual_interest = entry.get("actual_interest", "")

            # High-value if: escalated, or marked useful at any level
            # Previously was too restrictive (only useful + high/urgent predictions)
            # Now includes useful emails at medium level too, since user agreed with prediction
            if actual_interest == "more_important" or actual_interest == "useful":
                high_value.append(entry)

        return high_value

    def _analyze_category_preferences(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Analyze which categories appear most in high-value content"""
        category_scores = Counter()

        for entry in entries:
            ai_analysis = entry.get("ai_analysis", {})
            category = ai_analysis.get("category", "")

            if category:
                category_scores[category] += 1

        return dict(category_scores.most_common(10))

    def _analyze_technology_mentions(
        self, entries: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Analyze which technologies are mentioned in high-value content"""
        tech_scores = Counter()

        for entry in entries:
            ai_analysis = entry.get("ai_analysis", {})
            technologies = ai_analysis.get("technologies_mentioned", [])

            for tech in technologies:
                tech_scores[tech] += 1

        return dict(tech_scores.most_common(15))

    def _analyze_topic_patterns(self, entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze which topics are identified in high-value content"""
        topic_scores = Counter()

        for entry in entries:
            ai_analysis = entry.get("ai_analysis", {})
            topics = ai_analysis.get("topics_identified", [])

            for topic in topics:
                topic_scores[topic] += 1

        return dict(topic_scores.most_common(15))

    def export_learning_report(self, output_path: Optional[str] = None) -> str:
        """
        Export learning insights as markdown report

        Args:
            output_path: Optional path to save report

        Returns:
            Report as markdown string
        """
        entries = self.feedback_data.get("feedback_entries", [])

        if not entries:
            return "# Learning Report\n\nNo feedback data available yet."

        analysis = self.analyze_feedback_patterns()
        suggestions = self.generate_profile_suggestions()

        lines = []
        lines.append("# 🧠 AI Learning Analysis Report")
        lines.append(
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        )
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Feedback Entries:** {len(entries)}")
        lines.append(
            f"- **Overall Accuracy:** {self.feedback_data.get('stats', {}).get('current_accuracy', 'Unknown')}%"
        )
        lines.append("")

        # Accuracy by Level
        if analysis.get("accuracy_by_level"):
            lines.append("## Accuracy by Interest Level")
            lines.append("")
            for level, stats in analysis["accuracy_by_level"].items():
                lines.append(
                    f"- **{level.title()}:** {stats['accuracy']}% ({stats['accurate']}/{stats['total']} correct)"
                )
            lines.append("")

        # Time Trends
        if analysis.get("time_trends", {}).get("status") != "insufficient_data":
            trends = analysis.get("time_trends", {})
            lines.append("## Accuracy Trends")
            lines.append("")
            lines.append(f"- **Early Accuracy:** {trends.get('early_accuracy', 0)}%")
            lines.append(f"- **Recent Accuracy:** {trends.get('recent_accuracy', 0)}%")
            lines.append(f"- **Trend:** {trends.get('trend', 'unknown').title()}")
            lines.append(f"- **Improvement:** {trends.get('improvement', 0):+.1f}%")
            lines.append("")

        # Strongest and Weakest Areas
        if analysis.get("strongest_areas"):
            lines.append("## Strongest Areas (80%+ accurate)")
            lines.append("")
            for area in analysis["strongest_areas"]:
                lines.append(f"- {area.title()}")
            lines.append("")

        if analysis.get("weakest_areas"):
            lines.append("## Areas for Improvement (<60% accurate)")
            lines.append("")
            for area in analysis["weakest_areas"]:
                lines.append(f"- {area.title()}")
            lines.append("")

        # Profile Suggestions
        if suggestions.get("status") != "insufficient_data":
            lines.append("## 💡 Profile Suggestions")
            lines.append("")

            if suggestions.get("add_interests"):
                lines.append("### Interests to Add")
                lines.append("")
                for interest in suggestions["add_interests"]:
                    lines.append(f"- **{interest['interest']}** - {interest['reason']}")
                lines.append("")

            if suggestions.get("add_senders"):
                lines.append("### Trusted Senders to Add")
                lines.append("")
                for sender in suggestions["add_senders"]:
                    lines.append(f"- **{sender['sender']}** - {sender['reason']}")
                lines.append("")

            if suggestions.get("confidence_notes"):
                lines.append("### Confidence Notes")
                lines.append("")
                lines.append(f"> {suggestions['confidence_notes']}")
                lines.append("")

        # Top Senders
        if analysis.get("sender_patterns"):
            lines.append("## Top Senders")
            lines.append("")
            for sender, stats in list(analysis["sender_patterns"].items())[:5]:
                high_value_rate = stats.get("high_value_rate", 0)
                escalation_rate = stats.get("escalation_rate", 0)
                lines.append(
                    f"- **{sender}:** {stats['total_emails']} emails, {stats['accuracy']}% accurate prediction"
                )
                if high_value_rate > 0:
                    lines.append(
                        f"  - High-value content: {stats['high_value_emails']}/{stats['total_emails']} ({high_value_rate}%)"
                    )
                if escalation_rate > 0:
                    lines.append(
                        f"  - Escalations: {stats['escalated_emails']}/{stats['total_emails']} ({escalation_rate}%)"
                    )
            lines.append("")

        report = "\n".join(lines)

        # Save if path provided
        if output_path:
            try:
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(report)
                print(f"✅ Report saved to: {output_path}")
            except Exception as e:
                print(f"⚠️  Could not save report: {str(e)}")

        return report
