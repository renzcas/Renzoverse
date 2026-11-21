"""Loads only the checked-in Spine schemas by their stable contract names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from spine_runtime.contract_errors import SchemaLoadError, UnknownContractError


DEFAULT_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "renzoverse_spine"
SCHEMA_FILES = {
    "telemetry_contract": "telemetry_contract/schema.json",
    "world_contract": "world_contract/schema.json",
    "event_contract": "event_contract/schema.json",
    "command_contract": "command_contract/schema.json",
    "module_contract": "module_contract/schema.json",
}


def _reject_remote_refs(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        reference = value.get("$ref")
        if isinstance(reference, str) and not reference.startswith("#"):
            raise SchemaLoadError(
                f"Remote or external schema reference is not allowed at {path}: {reference}"
            )
        for key, child in value.items():
            _reject_remote_refs(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_remote_refs(child, f"{path}[{index}]")


class ContractLoader:
    """Load and check local JSON Schema Draft 2020-12 definitions."""

    def __init__(self, schema_dir: str | Path = DEFAULT_SCHEMA_DIR) -> None:
        self.schema_dir = Path(schema_dir).resolve()

    @property
    def contract_names(self) -> tuple[str, ...]:
        return tuple(SCHEMA_FILES)

    def load(self, contract_name: str) -> dict[str, Any]:
        try:
            relative_path = SCHEMA_FILES[contract_name]
        except KeyError as exc:
            raise UnknownContractError(f"Unknown contract: {contract_name}") from exc

        schema_path = (self.schema_dir / relative_path).resolve()
        if not schema_path.is_relative_to(self.schema_dir):
            raise SchemaLoadError(f"Schema path escapes configured directory: {schema_path}")

        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SchemaLoadError(
                f"Could not read schema '{contract_name}' from {schema_path}: {exc}"
            ) from exc

        if not isinstance(schema, dict):
            raise SchemaLoadError(f"Schema '{contract_name}' must be a JSON object.")
        _reject_remote_refs(schema)
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise SchemaLoadError(
                f"Schema '{contract_name}' is not valid Draft 2020-12: {exc.message}"
            ) from exc
        return schema
