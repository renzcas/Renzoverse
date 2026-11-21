"""Explicit errors raised by the Spine runtime."""


class ContractRuntimeError(RuntimeError):
    """Base class for runtime contract errors."""


class UnknownContractError(ContractRuntimeError):
    """The requested contract is not registered in this runtime."""


class SchemaLoadError(ContractRuntimeError):
    """A local contract schema could not be loaded or checked."""


class ContractValidationError(ContractRuntimeError):
    """A message does not satisfy its registered contract."""

    def __init__(self, contract_name: str, details: list[str]) -> None:
        self.contract_name = contract_name
        self.details = tuple(details)
        detail_text = "; ".join(self.details) or "message is invalid"
        super().__init__(f"{contract_name} validation failed: {detail_text}")


class RouteError(ContractRuntimeError):
    """A message cannot be routed to a registered handler."""


class RouteHandlerError(RouteError):
    """A registered handler failed while processing a valid message."""


class MockBusError(ContractRuntimeError):
    """A mock-bus fixture could not be read or used."""
