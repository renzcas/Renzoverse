"""Validated, in-process routing for Spine messages."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from spine_runtime.contract_errors import RouteError, RouteHandlerError
from spine_runtime.contract_validator import ContractValidator

MessageHandler = Callable[[Any], Any]


class ContractRouter:
    """Validate contract messages before synchronous handler dispatch."""

    def __init__(self, validator: ContractValidator) -> None:
        self.validator = validator
        self._handlers: dict[str, dict[str, MessageHandler]] = {}

    def register(
        self, contract_name: str, route_name: str, handler: MessageHandler
    ) -> None:
        if contract_name not in self.validator.contract_names:
            raise RouteError(f"Cannot register route for unknown contract: {contract_name}")
        if not route_name:
            raise RouteError("Route name must not be empty.")
        if not callable(handler):
            raise RouteError(f"Handler for route '{route_name}' is not callable.")

        handlers = self._handlers.setdefault(contract_name, {})
        if route_name in handlers:
            raise RouteError(
                f"Route '{route_name}' is already registered for '{contract_name}'."
            )
        handlers[route_name] = handler

    def dispatch(self, contract_name: str, message: Any) -> dict[str, Any]:
        self.validator.validate(contract_name, message)
        handlers = self._handlers.get(contract_name)
        if not handlers:
            raise RouteError(f"No routes registered for contract '{contract_name}'.")

        results: dict[str, Any] = {}
        for route_name, handler in handlers.items():
            try:
                results[route_name] = handler(message)
            except Exception as exc:
                raise RouteHandlerError(
                    f"Route '{route_name}' failed for contract '{contract_name}': {exc}"
                ) from exc
        return results
