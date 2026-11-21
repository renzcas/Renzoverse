"""Validate fixture fields needed by the viewer; this is not a browser test."""

from unittest import TestCase

from spine_runtime.contract_validator import ContractValidator
from spine_runtime.mock_bus import MockBus


class ViewerActivationTests(TestCase):
    def test_mock_snapshot_contains_valid_viewer_data_and_matching_world(self) -> None:
        validator = ContractValidator()
        bus = MockBus(validator)
        world = bus.read_channel("world_state")[0]
        snapshots = bus.read_channel("telemetry_stream")

        self.assertTrue(snapshots)
        for snapshot in snapshots:
            validator.validate("telemetry_contract", snapshot)
            self.assertEqual(snapshot["worldId"], world["worldId"])
            self.assertIsInstance(snapshot["threat"], (int, float))
            self.assertIsInstance(snapshot["cta"], (int, float))
            self.assertIsInstance(snapshot["corruption"], (int, float))
            self.assertIsInstance(snapshot["creatures"], list)
            for creature in snapshot["creatures"]:
                self.assertIsInstance(creature["entityId"], str)
                self.assertIsInstance(creature["hunger"], (int, float))
                self.assertIsInstance(creature["isAfraid"], bool)

        self.assertTrue(world["regions"])
