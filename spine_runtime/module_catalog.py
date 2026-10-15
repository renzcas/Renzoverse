"""Validated local catalog for module-contract manifests."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_validator import ContractValidator

CONTRACT_IDS = {
    "telemetry_contract": "urn:renzoverse:spine:telemetry:v1@1.0.0",
    "world_contract": "urn:renzoverse:spine:world:v1@1.0.0",
    "event_contract": "urn:renzoverse:spine:event:v1@1.0.0",
    "command_contract": "urn:renzoverse:spine:command:v1@1.0.0",
    "module_contract": "urn:renzoverse:spine:module:v1@1.0.0",
}


class ModuleCatalog:
    """Validate manifests and supported contract IDs without importing modules."""

    def __init__(self, validator: ContractValidator) -> None:
        self.validator = validator

    def load(self, manifests: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
        catalog: dict[str, Mapping[str, Any]] = {}
        supported_ids = set(CONTRACT_IDS.values())
        for index, manifest in enumerate(manifests):
            self.validator.validate("module_contract", manifest)
            module_id = manifest["moduleId"]
            if module_id in catalog:
                raise ContractValidationError(
                    "module_contract", [f"$[{index}].moduleId: duplicate module ID '{module_id}'"]
                )

            unsupported = sorted(set(manifest["contracts"]) - supported_ids)
            if unsupported:
                raise ContractValidationError(
                    "module_contract",
                    [
                        f"$[{index}].contracts: unsupported contract reference '{contract_id}'"
                        for contract_id in unsupported
                    ],
                )
            catalog[module_id] = manifest
        return catalog
