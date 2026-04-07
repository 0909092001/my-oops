import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from prediction_agents.config import Settings
from prediction_agents.models import LearningFeedback
from prediction_agents.pipeline import PredictionMarketResearchPipeline


class PipelineTestCase(unittest.TestCase):
    def setUp(self):
        self.settings = Settings.from_env()
        self.pipeline = PredictionMarketResearchPipeline(self.settings)

    def test_run_returns_ranked_traders_and_recommendation(self):
        result = self.pipeline.run(
            event_id="us-election-2028",
            question="Who should we copy for the election market?",
        )
        self.assertEqual(result["event"].event_id, "us-election-2028")
        self.assertGreaterEqual(len(result["polymarket_traders"]), 1)
        self.assertGreaterEqual(len(result["kalshi_traders"]), 1)
        self.assertGreaterEqual(len(result["recommendation"].recommended_traders), 1)

    def test_learning_loop_updates_scores(self):
        self.pipeline.run(event_id="us-election-2028", question="test question")
        before = {trader.trader_id: trader.learning_score for trader in self.pipeline.traders}
        updated = self.pipeline.learn(
            [
                LearningFeedback(
                    trader_id="poly_01",
                    event_id="us-election-2028",
                    actual_outcome="Candidate A wins",
                    copied=True,
                    profitable=True,
                    notes="Positive post-trade review",
                )
            ]
        )
        after = {trader.trader_id: trader.learning_score for trader in updated}
        self.assertGreater(after["poly_01"], before["poly_01"])


if __name__ == "__main__":
    unittest.main()
