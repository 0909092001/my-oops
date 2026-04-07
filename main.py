import json
import logging

from .config import Settings
from .models import LearningFeedback
from .pipeline import PredictionMarketResearchPipeline, render_summary


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = Settings.from_env()
    pipeline = PredictionMarketResearchPipeline(settings)
    result = pipeline.run(
        event_id="us-election-2028",
        question="Which traders should we copy for the election winner market?",
    )
    print(render_summary(result))

    feedback = [
        LearningFeedback(
            trader_id="poly_01",
            event_id="us-election-2028",
            actual_outcome="Candidate A wins",
            copied=True,
            profitable=True,
            notes="Copied the top politics specialist and realized profit.",
        )
    ]
    updated = pipeline.learn(feedback)
    snapshot = {
        trader.trader_id: {
            "display_name": trader.display_name,
            "learning_score": trader.learning_score,
            "last_feedback": trader.metadata.get("last_feedback", ""),
        }
        for trader in updated
    }
    print("")
    print("Learning loop snapshot:")
    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
