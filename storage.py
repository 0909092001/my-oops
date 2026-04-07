import json
from pathlib import Path
from typing import Dict, List

from .models import BetRecord, EventResearch, Trader


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class LocalKnowledgeStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def load_traders(self) -> List[Trader]:
        payload = _load_json(self.data_dir / "sample_traders.json")
        traders = []
        for item in payload:
            bets = [BetRecord(**bet) for bet in item["bets"]]
            trader = Trader(
                trader_id=item["trader_id"],
                platform=item["platform"],
                display_name=item["display_name"],
                wallet=item["wallet"],
                bets=bets,
                tags=item.get("tags", []),
                metadata=item.get("metadata", {}),
            )
            traders.append(trader)
        return traders

    def load_event_research(self) -> Dict[str, EventResearch]:
        payload = _load_json(self.data_dir / "sample_events.json")
        return {item["event_id"]: EventResearch(**item) for item in payload}
