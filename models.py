from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class BetRecord:
    event_id: str
    market_title: str
    niche: str
    predicted_side: str
    confidence: float
    stake: float
    pnl: float
    won: bool


@dataclass
class Trader:
    trader_id: str
    platform: str
    display_name: str
    wallet: str
    bets: List[BetRecord]
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    consistency_score: float = 0.0
    roi: float = 0.0
    win_rate: float = 0.0
    preferred_niches: List[str] = field(default_factory=list)
    learning_score: float = 0.0


@dataclass
class EventResearch:
    event_id: str
    title: str
    niche: str
    question: str
    summary: str
    sources: List[str]
    evidence_points: List[str]


@dataclass
class Recommendation:
    event_id: str
    recommended_traders: List[str]
    rationale: str
    risk_flags: List[str]


@dataclass
class LearningFeedback:
    trader_id: str
    event_id: str
    actual_outcome: str
    copied: bool
    profitable: bool
    notes: str
