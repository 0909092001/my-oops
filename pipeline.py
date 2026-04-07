from typing import Dict, List

from .agents.chat import TraderChatAgent
from .agents.event_research import EventResearchAgent
from .agents.learning_loop import LearningLoopAgent
from .agents.niche_mapper import NicheMappingAgent
from .agents.trader_discovery import KalshiDiscoveryAgent, PolymarketDiscoveryAgent
from .config import Settings
from .models import LearningFeedback, Trader
from .storage import LocalKnowledgeStore


class PredictionMarketResearchPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        store = LocalKnowledgeStore(settings.data_dir)
        self.traders = store.load_traders()
        self.local_events = store.load_event_research()
        self.polymarket_agent = PolymarketDiscoveryAgent()
        self.kalshi_agent = KalshiDiscoveryAgent()
        self.niche_agent = NicheMappingAgent()
        self.event_agent = EventResearchAgent(settings, self.local_events)
        self.chat_agent = TraderChatAgent(settings)
        self.learning_agent = LearningLoopAgent()

    def run(self, event_id: str, question: str) -> Dict[str, object]:
        polymarket = self.niche_agent.map_niches(self.polymarket_agent.discover(self.traders, top_n=3))
        kalshi = self.niche_agent.map_niches(self.kalshi_agent.discover(self.traders, top_n=3))
        combined = self._merge_unique(polymarket + kalshi)
        event = self.event_agent.enrich_event(event_id)
        recommendation = self.chat_agent.recommend(question, combined, event)
        return {
            "event": event,
            "polymarket_traders": polymarket,
            "kalshi_traders": kalshi,
            "recommendation": recommendation,
        }

    def learn(self, feedback_items: List[LearningFeedback]) -> List[Trader]:
        updated = self.learning_agent.apply_feedback(self.traders, feedback_items)
        return list(updated.values())

    @staticmethod
    def _merge_unique(traders: List[Trader]) -> List[Trader]:
        merged = []
        seen = set()
        for trader in traders:
            if trader.trader_id in seen:
                continue
            seen.add(trader.trader_id)
            merged.append(trader)
        return merged


def render_summary(result: Dict[str, object]) -> str:
    event = result["event"]
    recommendation = result["recommendation"]
    polymarket = result["polymarket_traders"]
    kalshi = result["kalshi_traders"]
    lines = [
        "Event: {0} ({1})".format(event.title, event.niche),
        "Question: {0}".format(event.question),
        "Research summary: {0}".format(event.summary),
        "",
        "Top Polymarket traders:",
    ]
    for trader in polymarket:
        lines.append("- {0} | score={1:.2f} | roi={2:.2f} | win_rate={3:.2f} | niches={4}".format(trader.display_name, trader.consistency_score, trader.roi, trader.win_rate, ", ".join(trader.preferred_niches)))
    lines.append("")
    lines.append("Top Kalshi traders:")
    for trader in kalshi:
        lines.append("- {0} | score={1:.2f} | roi={2:.2f} | win_rate={3:.2f} | niches={4}".format(trader.display_name, trader.consistency_score, trader.roi, trader.win_rate, ", ".join(trader.preferred_niches)))
    lines.append("")
    lines.append("Recommendation:")
    lines.append("- Traders to copy: {0}".format(", ".join(recommendation.recommended_traders)))
    lines.append("- Rationale: {0}".format(recommendation.rationale))
    lines.append("- Risk flags: {0}".format("; ".join(recommendation.risk_flags) if recommendation.risk_flags else "None"))
    return "\n".join(lines)
