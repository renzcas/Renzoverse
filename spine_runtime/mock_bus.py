"""Deterministic file-backed contract message fixtures."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from spine_runtime.contract_errors import ContractValidationError, MockBusError
from spine_runtime.contract_router import ContractRouter
from spine_runtime.contract_validator import ContractValidator
from spine_runtime.module_catalog import ModuleCatalog

DEFAULT_BUS_DIR = Path(__file__).resolve().parent / "mock_bus"
CHANNELS = {
    "telemetry_stream": ("telemetry_stream.json", "telemetry_contract", True),
    "world_state": ("world_state.json", "world_contract", False),
    "event_stream": ("event_stream.json", "event_contract", True),
    "module_stream": ("module_stream.json", "module_contract", True),
}


class MockBus:
    """Read and validate mock messages before publishing them through a router."""

    def __init__(
        self,
        validator: ContractValidator | None = None,
        bus_dir: str | Path = DEFAULT_BUS_DIR,
    ) -> None:
        self.validator = validator or ContractValidator()
        self.bus_dir = Path(bus_dir).resolve()

    @property
    def channel_names(self) -> tuple[str, ...]:
        return tuple(CHANNELS)

    def read_channel(self, channel: str) -> list[Any]:
        try:
            filename, contract_name, is_stream = CHANNELS[channel]
        except KeyError as exc:
            raise MockBusError(f"Unknown mock-bus channel: {channel}") from exc

        path = (self.bus_dir / filename).resolve()
        if not path.is_relative_to(self.bus_dir):
            raise MockBusError(f"Bus fixture escapes configured directory: {path}")
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise MockBusError(
                f"Could not read mock-bus channel '{channel}' from {path}: {exc}"
            ) from exc

        if is_stream:
            if not isinstance(value, list):
                raise MockBusError(f"Mock-bus stream '{channel}' must contain a JSON array.")
            messages = value
        else:
            messages = [value]

        for index, message in enumerate(messages):
            try:
                self.validator.validate(contract_name, message)
            except ContractValidationError as exc:
                raise MockBusError(
                    f"Invalid message at {channel}[{index}]: {exc}"
                ) from exc

        if channel == "module_stream":
            ModuleCatalog(self.validator).load(messages)
        return messages

    def publish_channel(
        self, channel: str, router: ContractRouter
    ) -> list[dict[str, Any]]:
        _, contract_name, _ = self._channel_definition(channel)
        messages = self.read_channel(channel)
        return [router.dispatch(contract_name, message) for message in messages]

    def publish_all(self, router: ContractRouter) -> dict[str, list[dict[str, Any]]]:
        return {
            channel: self.publish_channel(channel, router)
            for channel in self.channel_names
        }

    def iter_messages(self, channel: str) -> Iterator[Any]:
        yield from self.read_channel(channel)

    @staticmethod
    def _channel_definition(channel: str) -> tuple[str, str, bool]:
        try:
            return CHANNELS[channel]
        except KeyError as exc:
            raise MockBusError(f"Unknown mock-bus channel: {channel}") from exc
