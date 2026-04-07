import json
import logging
from typing import Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import Settings
from ..models import EventResearch


class EventResearchAgent:
    def __init__(self, settings: Settings, local_events: Dict[str, EventResearch]):
        self.settings = settings
        self.local_events = local_events
        self.logger = logging.getLogger(self.__class__.__name__)

    def enrich_event(self, event_id: str) -> EventResearch:
        if self.settings.apify_token:
            live = self._fetch_from_apify(event_id)
            if live is not None:
                return live
        if event_id not in self.local_events:
            raise KeyError("Unknown event_id: {0}".format(event_id))
        return self.local_events[event_id]

    def _fetch_from_apify(self, event_id: str) -> Optional[EventResearch]:
        if event_id not in self.local_events:
            return None

        seed_event = self.local_events[event_id]
        body = {
            "startUrls": [{"url": url} for url in seed_event.sources],
            "maxCrawlPages": min(len(seed_event.sources), 5),
        }
        payload = json.dumps(body).encode("utf-8")
        endpoint = "https://api.apify.com/v2/acts/{0}/runs?token={1}".format(
            self.settings.apify_actor_id,
            self.settings.apify_token,
        )
        request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=20) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, ValueError) as exc:
            self.logger.warning("APIFY request failed, using local fallback: %s", exc)
            return None

        run_data = raw.get("data", {})
        summary = "APIFY run started for {0}. Run id: {1}".format(seed_event.title, run_data.get("id", "unknown"))
        return EventResearch(
            event_id=seed_event.event_id,
            title=seed_event.title,
            niche=seed_event.niche,
            question=seed_event.question,
            summary=summary,
            sources=seed_event.sources,
            evidence_points=seed_event.evidence_points + ["Live APIFY run triggered successfully."],
        )
