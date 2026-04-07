from typing import Dict, Iterable

from ..models import LearningFeedback, Trader


class LearningLoopAgent:
    def apply_feedback(self, traders: Iterable[Trader], feedback_items: Iterable[LearningFeedback]) -> Dict[str, Trader]:
        by_id = {trader.trader_id: trader for trader in traders}
        for feedback in feedback_items:
            trader = by_id.get(feedback.trader_id)
            if trader is None:
                continue
            delta = 0.07 if feedback.profitable else -0.09
            if feedback.copied:
                delta += 0.03
            trader.learning_score = round(max(0.0, min(1.0, trader.learning_score + delta)), 4)
            trader.metadata["last_feedback"] = feedback.notes
            trader.metadata["last_event_id"] = feedback.event_id
            trader.metadata["last_outcome"] = feedback.actual_outcome
        return by_id
