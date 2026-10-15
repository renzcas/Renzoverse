"""Check the authored Phase 9 world source against the canonical schema."""

import json
from pathlib import Path
from unittest import TestCase

from spine_runtime.contract_validator import ContractValidator


class Phase9MetadataSourceTests(TestCase):
    def test_cavesharp_world_definition_is_canonical_and_has_unique_ids(self) -> None:
        root = Path(__file__).resolve().parents[2]
        world = json.loads((root / "shared/worlds/cavesharp.json").read_text(encoding="utf-8"))

        ContractValidator().validate("world_contract", world)
        self.assertEqual(world["worldId"], "renzoverse.cavesharp.primary")
        self.assertEqual(
            len({region["regionId"] for region in world["regions"]}),
            len(world["regions"]),
        )
        self.assertEqual(
            len({entity_type["entityTypeId"] for entity_type in world["entityTypes"]}),
            len(world["entityTypes"]),
        )
