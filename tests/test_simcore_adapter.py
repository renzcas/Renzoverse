import unittest

from spine_runtime.adapters import adapt_simcore_event
from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_router import ContractRouter
from spine_runtime.contract_validator import ContractValidator


class TestSimCoreAdapter(unittest.TestCase):
    def test_adapt_simcore_event_validates_and_routes(self) -> None:
        raw = {
            "schema_version": "1.0.0",
            "source": "Renzo-SimCore",
            "branch": "simcore-v02",
            "tick": 14,
            "dt": 1.0,
            "agent": {
                "id": 4,
                "name": "Keeper",
                "role": "Keeper",
                "goal_satisfied": False,
                "memory_size": 12,
            },
            "beliefs": {
                "threat": 0.20,
                "fear": 0.00,
                "panic": 0.00,
                "trust": 0.80,
                "calm": 0.98,
            },
            "metrics": {"resilience": 0.98},
        }

        validator = ContractValidator()
        adapted = adapt_simcore_event(
            raw,
            event_id="simcore-tick-14-agent-4",
            sequence=14,
            occurred_at="2026-11-19T10:30:00+00:00",
            validator=validator,
        )

        self.assertEqual(adapted["eventType"], "simcore.agent.state")
        self.assertEqual(adapted["sourceModuleId"], "Renzo-SimCore")
        self.assertEqual(adapted["payload"]["agentName"], "Keeper")
        self.assertAlmostEqual(adapted["payload"]["metrics"]["resilience"], 0.98)

        seen = []
        router = ContractRouter(validator)
        router.register("event_contract", "simcore_sink", seen.append)
        results = router.dispatch("event_contract", adapted)
        self.assertEqual(len(seen), 1)
        self.assertIn("simcore_sink", results)

    def test_adapt_simcore_event_rejects_missing_sequence(self) -> None:
        with self.assertRaises(ContractValidationError):
            adapt_simcore_event(
                {"tick": 0, "agent": {}, "beliefs": {}, "metrics": {}},
                event_id="bad-event",
                occurred_at="2026-11-19T10:30:00+00:00",
            )


if __name__ == "__main__":
    unittest.main()
