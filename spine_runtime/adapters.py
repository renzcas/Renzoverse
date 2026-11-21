"""Explicit transformations from known legacy shapes into Spine messages."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_validator import ContractValidator

_CREATURE_FIELDS = (
    "name",
    "health",
    "aggression",
    "hunger",
    "x",
    "y",
    "corruptionExposure",
    "isAfraid",
)
_SNAPSHOT_FIELDS = (
    "threat",
    "cta",
    "corruption",
    "ctaBoss",
    "directive",
    "creatures",
    "corruptionGrid",
)


def adapt_legacy_telemetry(
    legacy: Mapping[str, Any],
    *,
    world_id: str | None = None,
    tick: int | None = None,
    generated_at: str | None = None,
    entity_ids_by_name: Mapping[str, str] | None = None,
    validator: ContractValidator | None = None,
) -> dict[str, Any]:
    """Convert known flat telemetry only when required authoritative metadata is supplied."""
    if not isinstance(legacy, Mapping):
        raise ContractValidationError(
            "telemetry_contract", ["legacy payload must be an object"]
        )
    if not isinstance(entity_ids_by_name, Mapping):
        raise ContractValidationError(
            "telemetry_contract",
            ["entity_ids_by_name must map legacy creature names to stable IDs"],
        )
    if not isinstance(world_id, str) or not world_id:
        raise ContractValidationError(
            "telemetry_contract", ["$.worldId: caller must supply a non-empty stable world ID"]
        )
    if isinstance(tick, bool) or not isinstance(tick, int) or tick < 0:
        raise ContractValidationError(
            "telemetry_contract", ["$.tick: caller must supply a non-negative integer tick"]
        )
    if not isinstance(generated_at, str) or not generated_at:
        raise ContractValidationError(
            "telemetry_contract",
            ["$.generatedAt: caller must supply an RFC 3339 timestamp"],
        )
    missing_fields = [field for field in _SNAPSHOT_FIELDS if field not in legacy]
    if missing_fields:
        raise ContractValidationError(
            "telemetry_contract",
            [f"legacy payload is missing source field '{field}'" for field in missing_fields],
        )
    if not isinstance(legacy["creatures"], list):
        raise ContractValidationError(
            "telemetry_contract", ["$.creatures: legacy field must be an array"]
        )

    creatures: list[dict[str, Any]] = []
    used_entity_ids: set[str] = set()
    for index, creature in enumerate(legacy["creatures"]):
        if not isinstance(creature, Mapping):
            raise ContractValidationError(
                "telemetry_contract", [f"$.creatures[{index}]: expected an object"]
            )
        creature_fields: dict[str, Any] = {}
        missing_creature_fields: list[str] = []
        ambiguous_creature_fields: list[str] = []
        for field in _CREATURE_FIELDS:
            aliases = (field, field[0].upper() + field[1:])
            present_aliases = [alias for alias in aliases if alias in creature]
            if not present_aliases:
                missing_creature_fields.append(field)
            elif len(present_aliases) > 1:
                ambiguous_creature_fields.append(field)
            else:
                creature_fields[field] = creature[present_aliases[0]]
        if missing_creature_fields:
            fields = ", ".join(missing_creature_fields)
            raise ContractValidationError(
                "telemetry_contract",
                [f"$.creatures[{index}]: legacy creature is missing fields: {fields}"],
            )
        if ambiguous_creature_fields:
            fields = ", ".join(ambiguous_creature_fields)
            raise ContractValidationError(
                "telemetry_contract",
                [
                    f"$.creatures[{index}]: ambiguous casing for fields: {fields}"
                ],
            )

        name = creature_fields["name"]
        if not isinstance(name, str) or not entity_ids_by_name.get(name):
            raise ContractValidationError(
                "telemetry_contract",
                [
                    f"$.creatures[{index}].entityId: no caller-supplied stable ID "
                    f"for creature name {name!r}"
                ],
            )
        entity_id = entity_ids_by_name[name]
        if not isinstance(entity_id, str) or not entity_id:
            raise ContractValidationError(
                "telemetry_contract",
                [
                    f"$.creatures[{index}].entityId: stable ID for creature "
                    f"name {name!r} must be a non-empty string"
                ],
            )
        if entity_id in used_entity_ids:
            raise ContractValidationError(
                "telemetry_contract",
                [f"$.creatures[{index}].entityId: duplicate stable ID {entity_id!r}"],
            )
        used_entity_ids.add(entity_id)
        creatures.append(
            {
                "entityId": entity_id,
                **creature_fields,
            }
        )

    snapshot = {
        "schemaVersion": "1.0.0",
        "worldId": world_id,
        "tick": tick,
        "generatedAt": generated_at,
        **{field: legacy[field] for field in _SNAPSHOT_FIELDS if field != "creatures"},
        "creatures": creatures,
    }
    (validator or ContractValidator()).validate("telemetry_contract", snapshot)
    return snapshot
