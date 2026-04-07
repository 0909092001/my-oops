from typing import List

from ..models import Trader


class BaseDiscoveryAgent:
    platform = ""

    def discover(self, traders: List[Trader], top_n: int = 3) -> List[Trader]:
        scored = []
        for trader in traders:
            if trader.platform.lower() != self.platform.lower():
                continue
            wins = sum(1 for bet in trader.bets if bet.won)
            total = len(trader.bets) or 1
            stake_total = sum(bet.stake for bet in trader.bets) or 1.0
            pnl_total = sum(bet.pnl for bet in trader.bets)
            win_rate = wins / total
            roi = pnl_total / stake_total
            consistency = (win_rate * 0.6) + (min(total, 20) / 20.0 * 0.2) + (max(roi, 0.0) * 0.2)
            trader.win_rate = round(win_rate, 4)
            trader.roi = round(roi, 4)
            trader.consistency_score = round(consistency, 4)
            trader.learning_score = round((trader.learning_score + consistency) / 2.0, 4) if trader.learning_score else round(consistency, 4)
            scored.append(trader)
        scored.sort(key=lambda trader: (trader.consistency_score, trader.roi, trader.win_rate), reverse=True)
        return scored[:top_n]


class PolymarketDiscoveryAgent(BaseDiscoveryAgent):
    platform = "polymarket"


class KalshiDiscoveryAgent(BaseDiscoveryAgent):
    platform = "kalshi"
