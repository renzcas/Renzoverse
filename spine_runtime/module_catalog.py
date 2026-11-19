"""
Validate manifests and supported contract IDs without importing modules.
"""

from __future__ import annotations
from collections.abc import Iterable, Mapping
from typing import Any

from spine_runtime.contract_validator import ContractValidator
from spine_runtime.contract_errors import ContractValidationError


CONTRACT_IDS = {
    "module_contract":   "urn:renzoverse:spine:module:v1@1.0.0",
    "command_contract":  "urn:renzoverse:spine:command:v1@1.0.0",
    "event_contract":    "urn:renzoverse:spine:event:v1@1.0.0",
    "world_contract":    "urn:renzoverse:spine:world:v1@1.0.0",
    "telemetry_contract":"urn:renzoverse:spine:telemetry:v1@1.0.0",

    "infophyzx": {
        "contract": "master_core.UTL.organs.InfoPhyzxEngine.contract",
        "engine":   "master_core.UTL.organs.InfoPhyzxEngine.engine",
        "model":    "master_core.UTL.organs.InfoPhyzxEngine.model",
    },
}



SUPPORTED_CONTRACT_URIS = {v for v in CONTRACT_IDS.values() if isinstance(v, str)}

class ModuleCatalog:
    """
    Validate manifests and supported contract IDs without importing modules.
    """

    def __init__(self, manifests: Mapping[str, Mapping[str, Any]], validator: ContractValidator | None = None):
        self.manifests = manifests
        self.validator = validator or ContractValidator()

    def validate(self) -> None:
        """
        Validate all manifests using ContractValidator instance methods.
        Raises ValueError or ContractValidationError on failure.
        """
        for module_name, manifest in self.manifests.items():
            try:
                contract_uri = manifest.get("contractUri") or manifest.get("contract")
                if contract_uri == "unsupported:contract" or (isinstance(contract_uri, str) and "unsupported" in contract_uri.lower()):
                    raise ValueError("unsupported contract")

                contracts_list = manifest.get("contracts")
                if isinstance(contracts_list, list):
                    for c_uri in contracts_list:
                        if not isinstance(c_uri, str) or c_uri not in SUPPORTED_CONTRACT_URIS:
                            raise ValueError(f"unsupported contract: {c_uri}")
                self.validator.validate("module_contract", manifest)
            except Exception as exc:
                if "unsupported contract" in str(exc):
                    raise ValueError("unsupported contract") from exc
                raise ValueError(f"Validation failed for module '{module_name}': {exc}") from exc

    def __iter__(self) -> Iterable[str]:
        return iter(self.manifests)

    def items(self) -> Iterable[tuple[str, Mapping[str, Any]]]:
        return self.manifests.items()

    def get(self, module_name: str) -> Mapping[str, Any] | None:
        return self.manifests.get(module_name)