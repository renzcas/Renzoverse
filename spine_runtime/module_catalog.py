"""
Validate manifests and supported contract IDs without importing modules.
"""

from __future__ import annotations
from collections.abc import Iterable, Mapping
from typing import Any

from spine_runtime.contract_validator import ContractValidator
from spine_runtime.contract_errors import ContractValidationError


# ---------------------------------------------------------------------------
# Contract URN registry
# ---------------------------------------------------------------------------

CONTRACT_IDS = {
    "module_contract":   "urn:renzoverse:spine:module:v1@1.0.0",
    "command_contract":  "urn:renzoverse:spine:command:v1@1.0.0",
    "event_contract":    "urn:renzoverse:spine:event:v1@1.0.0",
    "world_contract":    "urn:renzoverse:spine:world:v1@1.0.0",
    "telemetry_contract":"urn:renzoverse:spine:telemetry:v1@1.0.0",

    # -----------------------------------------------------------------------
    # InfoPhyzx module registration (from your active tab)
    # -----------------------------------------------------------------------
    "infophyzx": {
        "contract": "master_core.UTL.organs.InfoPhyzxEngine.contract",
        "engine":   "master_core.UTL.organs.InfoPhyzxEngine.engine",
        "model":    "master_core.UTL.organs.InfoPhyzxEngine.model",
    },
}


# ---------------------------------------------------------------------------
# ModuleCatalog
# ---------------------------------------------------------------------------

class ModuleCatalog:
    """
    Validate manifests and supported contract IDs without importing modules.
    """

    def __init__(self, manifests: Mapping[str, Mapping[str, Any]]):
        self.manifests = manifests

    # -----------------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate all manifests using ContractValidator.
        Raises ContractValidationError on failure.
        """
        for module_name, manifest in self.manifests.items():
            try:
                ContractValidator.validate_manifest(
                    manifest=manifest,
                    contract_ids=CONTRACT_IDS
                )
            except ContractValidationError as exc:
                raise ContractValidationError(
                    f"Validation failed for module '{module_name}': {exc}"
                ) from exc

    # -----------------------------------------------------------------------
    # Iteration
    # -----------------------------------------------------------------------

    def __iter__(self) -> Iterable[str]:
        return iter(self.manifests)

    def items(self) -> Iterable[tuple[str, Mapping[str, Any]]]:
        return self.manifests.items()

    def get(self, module_name: str) -> Mapping[str, Any] | None:
        return self.manifests.get(module_name)
