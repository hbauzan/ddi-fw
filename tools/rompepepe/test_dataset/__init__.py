"""Test dataset package for rompepepe with auto-adaptation to active LanceDB corpus packs.
"""
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_seed_corpus() -> dict[str, Any]:
    json_path = Path(__file__).parent / "seed_corpus.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_categorized_dataset() -> list[dict[str, Any]]:
    """Returns structured dataset containing prompt, category, and expected verdict."""
    seed_data = load_seed_corpus()
    categories = seed_data.get("categories", {})
    dataset = []
    if categories:
        for cat_name, prompts in categories.items():
            expected = "PASS" if cat_name == "legitimate_python" else "BREACH"
            for p in prompts:
                dataset.append({"prompt": p, "category": cat_name, "expected": expected})
    else:
        for p in seed_data.get("positive_queries", []):
            dataset.append({"prompt": p, "category": "legitimate_python", "expected": "PASS"})
        for p in seed_data.get("negative_queries", []):
            dataset.append({"prompt": p, "category": "semantic_piggybacking", "expected": "BREACH"})
        for p in seed_data.get("boundary_blended_queries", []):
            dataset.append({"prompt": p, "category": "boundary_mutations", "expected": "BREACH"})
        for p in seed_data.get("edge_case_queries", []):
            dataset.append({"prompt": p, "category": "quorum_stress", "expected": "BREACH"})
    return dataset


async def build_adapted_corpus(firewall_client: Any) -> list[str]:
    """Constructs a comprehensive domain-aware adversarial test dataset."""
    cat_ds = get_categorized_dataset()
    if cat_ds:
        return [item["prompt"] for item in cat_ds]

    seed_data = load_seed_corpus()
    return (
        seed_data.get("positive_queries", [])
        + seed_data.get("negative_queries", [])
        + seed_data.get("boundary_blended_queries", [])
        + seed_data.get("edge_case_queries", [])
    )
