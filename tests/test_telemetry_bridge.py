import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from spine_runtime.contract_validator import ContractValidator
from spine_runtime.telemetry_bridge import build_snapshot, write_snapshot


class TelemetryBridgeTests(unittest.TestCase):
    def setUp(self):
        self.legacy = {
            "threat": 24,
            "cta": 18,
            "corruption": 12.5,
            "weather": "Storm",
            "ctaBoss": "Overlord-Alpha",
            "directive": "Monitor corruption nodes",
            "creatures": [
                {
                    "EntityId": "creature-001",
                    "Name": "TunnelRat",
                    "Health": 85,
                    "Aggression": 20,
                    "Hunger": 35,
                    "X": -8,
                    "Y": 4,
                    "CorruptionExposure": 3,
                    "IsAfraid": False,
                }
            ],
            "corruptionGrid": [[0.0, 0.5], [0.25, 0.0]],
        }
        self.generated_at = datetime(2026, 11, 5, tzinfo=timezone.utc)

    def test_builds_schema_valid_v1_snapshot_from_csharp_casing(self):
        snapshot = build_snapshot(
            self.legacy,
            "renzoverse.cavesharp.primary",
            7,
            self.generated_at,
        )

        ContractValidator().validate("telemetry_contract", snapshot)
        self.assertEqual(snapshot["tick"], 7)
        self.assertEqual(snapshot["weather"], "Storm")
        self.assertEqual(snapshot["creatures"][0]["entityId"], "creature-001")
        self.assertEqual(snapshot["creatures"][0]["name"], "TunnelRat")

    def test_requires_source_entity_identity(self):
        del self.legacy["creatures"][0]["EntityId"]
        with self.assertRaisesRegex(ValueError, "entityId"):
            build_snapshot(self.legacy, "renzoverse.cavesharp.primary", 1)

    def test_atomically_writes_snapshot_json(self):
        snapshot = build_snapshot(
            self.legacy,
            "renzoverse.cavesharp.primary",
            7,
            self.generated_at,
        )
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "cavesharp.v1.json"
            write_snapshot(output_path, snapshot)

            self.assertEqual(json.loads(output_path.read_text()), snapshot)
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()