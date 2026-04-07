from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    data_dir: Path
    openrouter_api_key: str
    openrouter_model: str
    apify_token: str
    apify_actor_id: str

    @classmethod
    def from_env(cls) -> "Settings":
        package_dir = Path(__file__).resolve().parent
        return cls(
            base_dir=package_dir,
            data_dir=package_dir / "data",
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            apify_token=os.getenv("APIFY_TOKEN", ""),
            apify_actor_id=os.getenv("APIFY_ACTOR_ID", "apify/website-content-crawler"),
        )
