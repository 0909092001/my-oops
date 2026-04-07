from collections import Counter
from typing import Iterable, List

from ..models import Trader


class NicheMappingAgent:
    def map_niches(self, traders: Iterable[Trader], max_niches: int = 3) -> List[Trader]:
        mapped = []
        for trader in traders:
            counts = Counter(bet.niche for bet in trader.bets)
            trader.preferred_niches = [name for name, _ in counts.most_common(max_niches)]
            mapped.append(trader)
        return mapped
