"""
Email Feedback Tracker
Records user feedback on email interest predictions for AI learning
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List


class EmailFeedbackTracker:
    """Tracks user feedback on email interest predictions"""

    def __init__(self):
        """Initialize feedback tracker"""
        self.feedback_log_path = "local_data/personal_data/email_feedback_log.json"
        self.feedback_data = self._load_feedback_log()

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.feedback_log_path), exist_ok=True)

    def _load_feedback_log(self) -> Dict[str, Any]:
        """Load existing feedback log"""
        if os.path.exists(self.feedback_log_path):
            try:
                with open(self.feedback_log_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load feedback log: {str(e)}")
                return self._get_empty_log()
        else:
            return self._get_empty_log()

    def _get_empty_log(self) -> Dict[str, Any]:
        """Get empty feedback log structure"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "feedback_entries": [],
            "stats": {
                "total_feedback_count": 0,
                "accurate_predictions": 0,
                "inaccurate_predictions": 0,
                "current_accuracy": 0.0,
            },
        }

    def _save_feedback_log(self):
        """Save feedback log to file"""
        try:
            with open(self.feedback_log_path, "w") as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving feedback log: {str(e)}")

    def record_feedback(
        self,
        email_subject: str,
        email_from: str,
        predicted_level: str,
        actual_interest: str,
        feedback_type: str,
        notes: str = "",
        ai_analysis: Dict[str, Any] = None,
    ) -> bool:
        """
        Record user feedback on an email prediction

        Args:
            email_subject: Subject of the email
            email_from: Sender email/name
            predicted_level: AI's predicted interest level
            actual_interest: User's actual interest (useful/not_interesting/more_important/less_important)
            feedback_type: Type of feedback (thumbs_up/thumbs_down/escalate/downgrade)
            notes: Optional user notes
            ai_analysis: Optional rich AI analysis data (category, key_points, technologies, etc.)

        Returns:
            True if feedback recorded successfully
        """
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "email_subject": email_subject,
                "email_from": email_from,
                "predicted_level": predicted_level,
                "actual_interest": actual_interest,
                "feedback_type": feedback_type,
                "notes": notes,
                "was_accurate": self._determine_accuracy(
                    predicted_level, actual_interest
                ),
            }

            # Add optional rich AI analysis if provided
            if ai_analysis:
                entry["ai_analysis"] = ai_analysis

            self.feedback_data["feedback_entries"].append(entry)
            self._update_stats()
            self._save_feedback_log()

            return True

        except Exception as e:
            print(f"❌ Error recording feedback: {str(e)}")
            return False

    def _determine_accuracy(self, predicted: str, actual: str) -> bool:
        """
        Determine if prediction was accurate based on user feedback

        Logic:
        - 'useful' = user agrees with the predicted priority level (ACCURATE)
        - 'not_interesting' = user thinks it should be lower priority (only accurate if LOW)
        - 'more_important' = user thinks it should be higher priority (INACCURATE)
        - 'less_important' = user thinks it should be lower priority (INACCURATE)

        Args:
            predicted: Predicted interest level (urgent, high, medium, low)
            actual: Actual user feedback (useful, not_interesting, more_important, less_important)

        Returns:
            True if prediction was accurate, False otherwise
        """
        # User agrees with prediction - always accurate regardless of level
        if actual == "useful":
            return True

        # User thinks it should be lower priority
        # Only accurate if we already predicted LOW (can't go lower)
        elif actual == "not_interesting":
            return predicted == "low"

        # User thinks it should be higher priority
        # Prediction was too low - never accurate
        elif actual == "more_important":
            return False

        # User thinks it should be lower priority
        # Prediction was too high - never accurate
        elif actual == "less_important":
            return False

        # Unknown feedback type
        else:
            return False

    def _update_stats(self):
        """Update accuracy statistics"""
        entries = self.feedback_data["feedback_entries"]
        total = len(entries)

        if total > 0:
            accurate = sum(1 for entry in entries if entry.get("was_accurate", False))
            accuracy = (accurate / total) * 100

            self.feedback_data["stats"] = {
                "total_feedback_count": total,
                "accurate_predictions": accurate,
                "inaccurate_predictions": total - accurate,
                "current_accuracy": round(accuracy, 1),
            }

    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Generate learning insights from feedback data

        Returns:
            Dict with insights, trends, and recommendations
        """
        entries = self.feedback_data["feedback_entries"]
        stats = self.feedback_data["stats"]

        if not entries:
            return {
                "message": "No feedback data yet. Start providing feedback to see insights!",
                "stats": stats,
                "recommendations": [],
            }

        insights = {
            "stats": stats,
            "trends": self._analyze_trends(entries),
            "sender_patterns": self._analyze_sender_patterns(entries),
            "recommendations": self._generate_recommendations(entries, stats),
        }

        return insights

    def _analyze_trends(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze feedback trends"""
        if not entries:
            return {}

        # Get recent entries (last 20)
        recent = entries[-20:] if len(entries) > 20 else entries

        recent_accurate = sum(1 for e in recent if e.get("was_accurate", False))
        recent_accuracy = (recent_accurate / len(recent)) * 100 if recent else 0

        # Compare to overall accuracy
        overall_accuracy = self.feedback_data["stats"]["current_accuracy"]
        trend = (
            "improving"
            if recent_accuracy > overall_accuracy
            else "stable"
            if recent_accuracy == overall_accuracy
            else "declining"
        )

        return {
            "recent_accuracy": round(recent_accuracy, 1),
            "overall_accuracy": overall_accuracy,
            "trend": trend,
            "recent_feedback_count": len(recent),
        }

    def _analyze_sender_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze patterns by sender"""
        sender_stats = {}

        for entry in entries:
            sender = entry.get("email_from", "Unknown")
            if sender not in sender_stats:
                sender_stats[sender] = {"total": 0, "accurate": 0, "useful_count": 0}

            sender_stats[sender]["total"] += 1
            if entry.get("was_accurate", False):
                sender_stats[sender]["accurate"] += 1
            if entry.get("actual_interest") == "useful":
                sender_stats[sender]["useful_count"] += 1

        # Convert to list and calculate accuracy
        patterns = []
        for sender, stats in sender_stats.items():
            accuracy = (
                (stats["accurate"] / stats["total"] * 100) if stats["total"] > 0 else 0
            )
            patterns.append(
                {
                    "sender": sender,
                    "total_emails": stats["total"],
                    "accuracy": round(accuracy, 1),
                    "useful_emails": stats["useful_count"],
                }
            )

        # Sort by total emails (most frequent senders first)
        patterns.sort(key=lambda x: x["total_emails"], reverse=True)

        return patterns[:10]  # Top 10 senders

    def _generate_recommendations(
        self, entries: List[Dict[str, Any]], stats: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on feedback"""
        recommendations = []

        accuracy = stats.get("current_accuracy", 0)

        if accuracy < 60:
            recommendations.append(
                "🔄 Accuracy is low. Update your interest profile with current interests and projects."
            )
        elif accuracy < 75:
            recommendations.append(
                "📈 Good progress! Continue providing feedback to improve accuracy."
            )
        elif accuracy >= 85:
            recommendations.append(
                "🎯 Excellent accuracy! The AI understands your preferences well."
            )

        # Check for specific patterns
        frequent_misses = [e for e in entries[-20:] if not e.get("was_accurate", False)]

        if len(frequent_misses) > 10:
            recommendations.append(
                "⚠️  Many recent mispredictions. Consider reviewing your interest profile."
            )

        # Check if enough feedback provided
        if stats.get("total_feedback_count", 0) < 20:
            recommendations.append(
                "📊 Provide more feedback (20+ emails) for better AI learning."
            )

        return recommendations

    def generate_feedback_report(self) -> str:
        """
        Generate a markdown report of feedback and learning insights

        Returns:
            Markdown formatted report
        """
        insights = self.get_learning_insights()
        lines = []

        lines.append("# Email Digest Learning Report")
        lines.append(
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        )
        lines.append("")

        # Stats
        lines.append("## Overall Statistics")
        lines.append("")
        stats = insights["stats"]
        lines.append(
            f"- **Total Feedback:** {stats.get('total_feedback_count', 0)} emails"
        )
        lines.append(
            f"- **Accurate Predictions:** {stats.get('accurate_predictions', 0)}"
        )
        lines.append(
            f"- **Inaccurate Predictions:** {stats.get('inaccurate_predictions', 0)}"
        )
        lines.append(f"- **Current Accuracy:** {stats.get('current_accuracy', 0)}%")
        lines.append("")

        # Trends
        if "trends" in insights:
            lines.append("## Trends")
            lines.append("")
            trends = insights["trends"]
            lines.append(f"- **Recent Accuracy:** {trends.get('recent_accuracy', 0)}%")
            lines.append(f"- **Trend:** {trends.get('trend', 'unknown').title()}")
            lines.append("")

        # Sender patterns
        if "sender_patterns" in insights:
            patterns = insights["sender_patterns"]
            if patterns:
                lines.append("## Top Senders")
                lines.append("")
                for pattern in patterns[:5]:
                    sender = pattern["sender"]
                    total = pattern["total_emails"]
                    accuracy = pattern["accuracy"]
                    useful = pattern["useful_emails"]
                    lines.append(
                        f"- **{sender}:** {total} emails, {accuracy}% accurate, {useful} useful"
                    )
                lines.append("")

        # Recommendations
        if "recommendations" in insights:
            recs = insights["recommendations"]
            if recs:
                lines.append("## Recommendations")
                lines.append("")
                for rec in recs:
                    lines.append(f"- {rec}")
                lines.append("")

        return "\n".join(lines)
