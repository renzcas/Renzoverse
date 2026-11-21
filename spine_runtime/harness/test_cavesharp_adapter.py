"""CaveSharp-to-Spine adapter rejection and transformation tests."""

from copy import deepcopy
from unittest import TestCase

from spine_runtime.adapters import adapt_legacy_telemetry
from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_validator import ContractValidator
from spine_runtime.mock_bus import MockBus


def legacy_snapshot() -> dict:
    return {
        "threat": 24,
        "cta": 18,
        "corruption": 12.5,
        "ctaBoss": "CaveSharp Fixture",
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


def adapt(
    legacy: dict,
    *,
    world_id: str | None = "renzoverse.mock.cave",
    tick: int | None = 42,
    generated_at: str | None = "2026-10-15T17:00:00Z",
    entity_ids_by_name: dict[str, str] | None = None,
) -> dict:
    return adapt_legacy_telemetry(
        legacy,
        world_id=world_id,
        tick=tick,
        generated_at=generated_at,
        entity_ids_by_name=entity_ids_by_name
        if entity_ids_by_name is not None
        else {"TunnelRat": "creature.tunnel-rat.001"},
        validator=ContractValidator(),
    )


class CaveSharpAdapterTests(TestCase):
    def test_converts_legacy_snapshot_to_contract_shaped_telemetry(self) -> None:
        snapshot = adapt(legacy_snapshot())

        ContractValidator().validate("telemetry_contract", snapshot)
        self.assertEqual(snapshot["schemaVersion"], "1.0.0")
        self.assertEqual(snapshot["worldId"], "renzoverse.mock.cave")
        self.assertEqual(snapshot["tick"], 42)
        self.assertEqual(
            snapshot["creatures"][0]["entityId"], "creature.tunnel-rat.001"
        )

    def test_normalizes_pinned_pascal_case_creature_properties(self) -> None:
        legacy = legacy_snapshot()
        legacy["creatures"][0] = {
            field[0].upper() + field[1:]: value
            for field, value in legacy["creatures"][0].items()
        }

        snapshot = adapt(legacy)

        self.assertEqual(
            snapshot["creatures"][0],
            {
                "entityId": "creature.tunnel-rat.001",
                **legacy_snapshot()["creatures"][0],
            },
        )
        ContractValidator().validate("telemetry_contract", snapshot)

    def test_rejects_ambiguous_creature_property_casing(self) -> None:
        legacy = legacy_snapshot()
        legacy["creatures"][0]["Name"] = "DifferentTunnelRat"

        with self.assertRaisesRegex(ContractValidationError, "ambiguous casing"):
            adapt(legacy)

    def test_rejects_each_missing_legacy_overseer_or_corruption_field(self) -> None:
        for field in (
            "threat",
            "cta",
            "corruption",
            "ctaBoss",
            "directive",
            "corruptionGrid",
            "creatures",
        ):
            with self.subTest(field=field):
                legacy = legacy_snapshot()
                del legacy[field]
                with self.assertRaisesRegex(ContractValidationError, field):
                    adapt(legacy)

    def test_rejects_missing_creature_fields(self) -> None:
        for field in (
            "name",
            "health",
            "aggression",
            "hunger",
            "x",
            "y",
            "corruptionExposure",
            "isAfraid",
        ):
            with self.subTest(field=field):
                legacy = legacy_snapshot()
                del legacy["creatures"][0][field]
                with self.assertRaisesRegex(ContractValidationError, field):
                    adapt(legacy)

    def test_rejects_missing_world_id(self) -> None:
        with self.assertRaisesRegex(ContractValidationError, "worldId"):
            adapt(legacy_snapshot(), world_id=None)

    def test_rejects_missing_or_invalid_tick(self) -> None:
        for tick in (None, -1, True, 1.5):
            with self.subTest(tick=tick):
                with self.assertRaisesRegex(ContractValidationError, "tick"):
                    adapt(legacy_snapshot(), tick=tick)

    def test_rejects_missing_or_invalid_timestamp(self) -> None:
        for generated_at in (None, "", "not-a-time"):
            with self.subTest(generated_at=generated_at):
                with self.assertRaisesRegex(ContractValidationError, "generatedAt"):
                    adapt(legacy_snapshot(), generated_at=generated_at)

    def test_rejects_missing_or_duplicate_stable_entity_ids(self) -> None:
        with self.assertRaisesRegex(ContractValidationError, "stable ID"):
            adapt(legacy_snapshot(), entity_ids_by_name={})

        with self.assertRaisesRegex(ContractValidationError, "non-empty string"):
            adapt(
                legacy_snapshot(),
                entity_ids_by_name={"TunnelRat": ["not", "a", "stable", "ID"]},
            )

        with self.assertRaisesRegex(ContractValidationError, "entity_ids_by_name"):
            adapt_legacy_telemetry(
                legacy_snapshot(),
                world_id="renzoverse.mock.cave",
                tick=42,
                generated_at="2026-10-15T17:00:00Z",
                entity_ids_by_name=None,
            )

        legacy = legacy_snapshot()
        legacy["creatures"].append(deepcopy(legacy["creatures"][0]))
        with self.assertRaisesRegex(ContractValidationError, "duplicate stable ID"):
            adapt(legacy)

    def test_rejects_malformed_top_level_and_nested_shapes(self) -> None:
        with self.assertRaisesRegex(ContractValidationError, "payload must be an object"):
            adapt_legacy_telemetry(
                [],
                world_id="renzoverse.mock.cave",
                tick=1,
                generated_at="2026-10-15T17:00:00Z",
                entity_ids_by_name={},
            )

        malformed = legacy_snapshot()
        malformed["creatures"] = {"name": "TunnelRat"}
        with self.assertRaisesRegex(ContractValidationError, "array"):
            adapt(malformed)

        malformed = legacy_snapshot()
        malformed["creatures"] = [None]
        with self.assertRaisesRegex(ContractValidationError, "expected an object"):
            adapt(malformed)

    def test_rejects_malformed_field_types_and_corruption_grid_shape(self) -> None:
        malformed = legacy_snapshot()
        malformed["threat"] = "high"
        with self.assertRaisesRegex(ContractValidationError, "threat"):
            adapt(malformed)

        malformed = legacy_snapshot()
        malformed["creatures"][0]["isAfraid"] = "false"
        with self.assertRaisesRegex(ContractValidationError, "isAfraid"):
            adapt(malformed)

        malformed = legacy_snapshot()
        malformed["corruptionGrid"] = [[0.0], "not-a-row"]
        with self.assertRaisesRegex(ContractValidationError, "corruptionGrid"):
            adapt(malformed)

    def test_rejects_world_definition_missing_region_identity(self) -> None:
        world = MockBus().read_channel("world_state")[0]
        world["regions"][0].pop("regionId")

        with self.assertRaisesRegex(ContractValidationError, "regionId"):
            ContractValidator().validate("world_contract", world)

    def test_adapter_does_not_invent_region_or_overseer_data(self) -> None:
        legacy = legacy_snapshot()
        legacy.pop("ctaBoss")
        with self.assertRaisesRegex(ContractValidationError, "ctaBoss"):
            adapt(legacy)

        world = MockBus().read_channel("world_state")[0]
        self.assertNotIn("regions", adapt(legacy_snapshot()))
        self.assertIn("regions", world)
