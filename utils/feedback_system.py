from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field

@dataclass
class FeedbackEntry:
    interaction_id: str
    feedback: Dict[str, Any]
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    
class FeedbackSystem:
    def __init__(self):
        self.feedback_history: List[FeedbackEntry] = []
        
    async def record_feedback(self, interaction_id: str, feedback: Dict[str, Any], context: Dict[str, Any] = None):
        """Passively record feedback without modifying system behavior"""
        entry = FeedbackEntry(
            interaction_id=interaction_id,
            feedback=feedback,
            timestamp=datetime.now(),
            context=context or {}
        )
        self.feedback_history.append(entry)
        logging.info(f"Recorded feedback for interaction {interaction_id}")
        
    async def get_feedback_stats(self, time_window: timedelta = None) -> Dict[str, Any]:
        """Get statistical summary of recorded feedback"""
        relevant_feedback = self.feedback_history
        if time_window:
            cutoff = datetime.now() - time_window
            relevant_feedback = [f for f in self.feedback_history if f.timestamp > cutoff]
            
        return {
            'total_entries': len(relevant_feedback),
            'average_rating': sum(f.feedback.get('rating', 0) for f in relevant_feedback) / len(relevant_feedback) if relevant_feedback else 0,
            'feedback_count_by_type': self._count_feedback_types(relevant_feedback)
        }
        
    def _count_feedback_types(self, feedback_entries: List[FeedbackEntry]) -> Dict[str, int]:
        """Count occurrences of different feedback types"""
        type_counts = {}
        for entry in feedback_entries:
            feedback_type = entry.feedback.get('type', 'unspecified')
            type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1
        return type_counts 