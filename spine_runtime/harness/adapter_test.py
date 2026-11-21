"""Test explicit conversion from legacy telemetry to the canonical snapshot."""

from unittest import TestCase

from spine_runtime.adapters import adapt_legacy_telemetry
from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_validator import ContractValidator


class TelemetryAdapterTests(TestCase):
    def test_legacy_payload_requires_explicit_identity_and_clock_metadata(self) -> None:
        legacy = {
            "threat": 24,
            "cta": 18,
            "corruption": 12.5,
            "ctaBoss": "Telemetry Mock",
            "directive": "Observe the cave",
            "creatures": [
                {
                    "name": "TunnelRat",
                    "health": 85,
                    "aggression": 20,
                    "hunger": 35,
                    "x": -8,
                    "y": 4,
                    "corruptionExposure": 3,
                    "isAfraid": False,
                }
            ],
            "corruptionGrid": [[0.0, 0.5]],
        }

        snapshot = adapt_legacy_telemetry(
            legacy,
            world_id="renzoverse.mock.cave",
            tick=42,
            generated_at="2026-10-15T17:00:00Z",
            entity_ids_by_name={"TunnelRat": "creature.tunnel-rat.001"},
        )

        ContractValidator().validate("telemetry_contract", snapshot)
        self.assertEqual(snapshot["worldId"], "renzoverse.mock.cave")
        self.assertEqual(snapshot["tick"], 42)
        self.assertEqual(
            snapshot["creatures"][0]["entityId"], "creature.tunnel-rat.001"
        )

    def test_adapter_rejects_missing_stable_creature_identity(self) -> None:
        legacy = {
            "threat": 0,
            "cta": 0,
            "corruption": 0,
            "ctaBoss": "Fixture",
            "directive": "Observe",
            "creatures": [
                {
                    "name": "TunnelRat",
                    "health": 85,
                    "aggression": 20,
                    "hunger": 35,
                    "x": -8,
                    "y": 4,
                    "corruptionExposure": 3,
                    "isAfraid": False,
                }
            ],
            "corruptionGrid": [],
        }

        with self.assertRaisesRegex(ContractValidationError, "stable ID"):
            adapt_legacy_telemetry(
                legacy,
                world_id="renzoverse.mock.cave",
                tick=1,
                generated_at="2026-10-15T17:00:00Z",
                entity_ids_by_name={},
            )
