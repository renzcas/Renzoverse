"""Validates runtime messages against the checked-in Spine JSON Schemas."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_loader import ContractLoader


def _reject_non_finite(
    contract_name: str, value: Any, path: str = "$"
) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractValidationError(
            contract_name, [f"{path}: non-finite numbers are not valid JSON values"]
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_non_finite(contract_name, child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_non_finite(contract_name, child, f"{path}[{index}]")


class ContractValidator:
    """Check schemas at construction and validate JSON-compatible messages."""

    def __init__(self, loader: ContractLoader | None = None) -> None:
        self.loader = loader or ContractLoader()
        self._validators: dict[str, Draft202012Validator] = {}
        for contract_name in self.loader.contract_names:
            schema = self.loader.load(contract_name)
            self._validators[contract_name] = Draft202012Validator(
                schema, format_checker=FormatChecker()
            )

    @property
    def contract_names(self) -> tuple[str, ...]:
        return tuple(self._validators)

    def validate(self, contract_name: str, message: Any) -> None:
        try:
            validator = self._validators[contract_name]
        except KeyError as exc:
            raise ContractValidationError(
                contract_name, ["contract is not registered in this validator"]
            ) from exc

        _reject_non_finite(contract_name, message)
        errors = sorted(
            validator.iter_errors(message),
            key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
        )
        if errors:
            details = [
                f"{self._format_path(error.absolute_path)}: {error.message}"
                for error in errors
            ]
            raise ContractValidationError(contract_name, details)

    @staticmethod
    def _format_path(parts: Sequence[Any]) -> str:
        path = "$"
        for part in parts:
            if isinstance(part, int):
                path += f"[{part}]"
            else:
                path += f".{part}"
        return path
