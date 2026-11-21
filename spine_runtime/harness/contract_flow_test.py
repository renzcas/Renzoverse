"""Exercise fixture loading, validation, and in-process routing end to end."""

import copy
import math

from unittest import TestCase

from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_router import ContractRouter
from spine_runtime.contract_validator import ContractValidator
from spine_runtime.mock_bus import MockBus


class ContractFlowTests(TestCase):
    def test_all_mock_bus_channels_route_valid_messages(self) -> None:
        validator = ContractValidator()
        router = ContractRouter(validator)
        received: dict[str, list[object]] = {
            name: [] for name in validator.contract_names
        }

        for contract_name in validator.contract_names:
            router.register(
                contract_name,
                f"test.{contract_name}",
                lambda message, key=contract_name: received[key].append(message),
            )

        results = MockBus(validator).publish_all(router)

        self.assertEqual(len(results["telemetry_stream"]), 1)
        self.assertEqual(len(results["world_state"]), 1)
        self.assertEqual(len(results["event_stream"]), 1)
        self.assertEqual(len(results["module_stream"]), 2)
        self.assertEqual(len(received["telemetry_contract"]), 1)
        self.assertEqual(len(received["world_contract"]), 1)
        self.assertEqual(len(received["event_contract"]), 1)
        self.assertEqual(len(received["module_contract"]), 2)

    def test_router_rejects_invalid_message_before_handler(self) -> None:
        validator = ContractValidator()
        router = ContractRouter(validator)
        received = []
        router.register("telemetry_contract", "test.viewer", received.append)

        with self.assertRaises(ContractValidationError):
            router.dispatch("telemetry_contract", {"schemaVersion": "0.0.1"})

        self.assertEqual(received, [])

    def test_validator_rejects_non_finite_json_numbers(self) -> None:
        validator = ContractValidator()
        snapshot = copy.deepcopy(MockBus(validator).read_channel("telemetry_stream")[0])
        snapshot["corruption"] = math.nan

        with self.assertRaisesRegex(ContractValidationError, "non-finite"):
            validator.validate("telemetry_contract", snapshot)
