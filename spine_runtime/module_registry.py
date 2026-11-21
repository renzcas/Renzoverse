"""Load the local engine registry and report read-only module status."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_validator import ContractValidator


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_PATH = ROOT / "renzoverse.json"
REGISTRY_SCHEMA_PATH = ROOT / "renzoverse_spine" / "registry_manifest" / "schema.json"
CONTRACT_NAMES = {
    "urn:renzoverse:spine:telemetry:v1@1.0.0": "telemetry_contract",
}


class ModuleRegistry:
    """Validate the control-plane manifest and calculate module status on demand."""

    def __init__(
        self,
        registry_path: str | Path = DEFAULT_REGISTRY_PATH,
        root: str | Path | None = None,
        validator: ContractValidator | None = None,
    ) -> None:
        self.registry_path = Path(registry_path).resolve()
        self.root = Path(root).resolve() if root else self.registry_path.parent
        self.validator = validator or ContractValidator()
        schema = json.loads(REGISTRY_SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self._schema_validator = Draft202012Validator(
            schema, format_checker=FormatChecker()
        )
        self.manifest = self._load_manifest()

    def list_status(self) -> dict[str, Any]:
        return {
            "project": self.manifest["project"],
            "version": self.manifest["version"],
            "modules": [
                self.module_status(module_id)
                for module_id in sorted(self.manifest["modules"])
            ],
        }

    def module_status(self, module_id: str) -> dict[str, Any]:
        try:
            module = self.manifest["modules"][module_id]
        except KeyError as exc:
            raise KeyError(f"Unknown module: {module_id}") from exc

        repository_path = self._resolve_local_path(module["path"])
        repository_exists = repository_path is not None and repository_path.is_dir()
        entry_point_path = (
            self._resolve_local_path(str(Path(module["path"]) / module["entry_point"]))
            if repository_path is not None
            else None
        )
        entry_point_exists = entry_point_path is not None and entry_point_path.is_file()
        prerequisites = []
        missing_prerequisite = False
        for prerequisite in module["prerequisites"]:
            executable = shutil.which(prerequisite["command"])
            if executable is None:
                missing_prerequisite = True
            prerequisites.append(
                {
                    "command": prerequisite["command"],
                    "minimum_version": prerequisite["minimum_version"],
                    "state": "present_unverified" if executable else "missing",
                }
            )

        telemetry = self._telemetry_status(module["telemetry_source"])
        blocked = not repository_exists or not entry_point_exists or missing_prerequisite
        return {
            "id": module_id,
            "name": module["name"],
            "status": "blocked" if blocked else "declared",
            "repository": {
                "path": module["path"],
                "state": "present" if repository_exists else "missing",
            },
            "entry_point": {
                "path": module["entry_point"],
                "state": "present" if entry_point_exists else "missing",
            },
            "prerequisites": prerequisites,
            "process": {"state": "not_managed"},
            "telemetry": telemetry,
        }

    def _load_manifest(self) -> dict[str, Any]:
        try:
            manifest = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not load registry manifest: {exc}") from exc
        errors = sorted(
            self._schema_validator.iter_errors(manifest),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        if errors:
            details = "; ".join(
                f"{list(error.absolute_path)}: {error.message}" for error in errors
            )
            raise ValueError(f"Invalid registry manifest: {details}")
        return manifest

    def _resolve_local_path(self, relative_path: str) -> Path | None:
        path = (self.root / relative_path).resolve()
        return path if path.is_relative_to(self.root) else None

    def _telemetry_status(self, source: dict[str, str]) -> dict[str, str]:
        path = self._resolve_local_path(source["path"])
        if path is None:
            return {"path": source["path"], "state": "invalid_path"}
        if not path.is_file():
            return {"path": source["path"], "state": "missing"}

        contract_name = CONTRACT_NAMES.get(source["contract"])
        if contract_name is None:
            return {"path": source["path"], "state": "unsupported_contract"}
        try:
            message = json.loads(path.read_text(encoding="utf-8"))
            self.validator.validate(contract_name, message)
        except ContractValidationError:
            return {"path": source["path"], "state": "invalid"}
        except (OSError, UnicodeError, json.JSONDecodeError):
            return {"path": source["path"], "state": "invalid"}
        return {"path": source["path"], "state": "valid"}