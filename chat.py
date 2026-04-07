import json
from dataclasses import asdict
from typing import Iterable, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import Settings
from ..models import EventResearch, Recommendation, Trader


class TraderChatAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    def recommend(self, question: str, traders: Iterable[Trader], event: EventResearch) -> Recommendation:
        ranked = sorted(
            traders,
            key=lambda trader: (
                event.niche in trader.preferred_niches,
                trader.learning_score,
                trader.consistency_score,
                trader.roi,
            ),
            reverse=True,
        )
        top = ranked[:3]
        rationale = self._recommend_with_openrouter(question, top, event) if self.settings.openrouter_api_key else self._recommend_locally(question, top, event)
        return Recommendation(
            event_id=event.event_id,
            recommended_traders=[trader.display_name for trader in top],
            rationale=rationale,
            risk_flags=self._risk_flags(top, event),
        )

    def _recommend_locally(self, question: str, traders: List[Trader], event: EventResearch) -> str:
        if not traders:
            return "No copy-trading recommendation is available because no traders matched the event context."
        leader = traders[0]
        summary = [
            "Top copy-trading candidates are ranked by niche fit, learning score, consistency score, and ROI.",
            "{0} leads for {1} because the trader shows learning={2:.2f}, consistency={3:.2f}, ROI={4:.2f}, and niches={5}.".format(
                leader.display_name,
                event.niche,
                leader.learning_score,
                leader.consistency_score,
                leader.roi,
                ", ".join(leader.preferred_niches),
            ),
        ]
        if len(traders) > 1:
            runner_up = traders[1]
            summary.append(
                "{0} is the next best copy candidate with win_rate={1:.2f} and niches={2}.".format(
                    runner_up.display_name,
                    runner_up.win_rate,
                    ", ".join(runner_up.preferred_niches),
                )
            )
        summary.append("Question asked: {0}".format(question))
        summary.append("Research summary: {0}".format(event.summary))
        return " ".join(summary)

    def _recommend_with_openrouter(self, question: str, traders: List[Trader], event: EventResearch) -> str:
        prompt = {
            "model": self.settings.openrouter_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a prediction-market analyst. Recommend which traders to copy using the supplied event research and trader metrics.",
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "question": question,
                            "event": asdict(event),
                            "traders": [asdict(trader) for trader in traders],
                        }
                    ),
                },
            ],
        }
        body = json.dumps(prompt).encode("utf-8")
        request = Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=body,
            headers={
                "Authorization": "Bearer {0}".format(self.settings.openrouter_api_key),
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"].strip()
        except (HTTPError, URLError, ValueError, KeyError):
            return self._recommend_locally(question, traders, event)

    def _risk_flags(self, traders: List[Trader], event: EventResearch) -> List[str]:
        if not traders:
            return ["No traders available for this event."]
        flags = []
        if any(event.niche not in trader.preferred_niches for trader in traders[:2]):
            flags.append("Some recommended traders have weaker niche specialization for this event.")
        if any(trader.roi < 0.1 for trader in traders):
            flags.append("At least one candidate has only a modest ROI edge.")
        if "will" in event.question.lower():
            flags.append("Binary prediction markets can reprice sharply near resolution.")
        return flags
