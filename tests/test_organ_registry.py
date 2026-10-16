import tempfile
import unittest
from pathlib import Path

from orchestrator.organ_contract import OrganRequest, OrganResponse
from orchestrator.registry import OrganLoadError, OrganRegistry, discover_organs


class OrganContractTests(unittest.TestCase):
    def test_request_validates_payload_and_context_tags(self) -> None:
        with self.assertRaises(TypeError):
            OrganRequest(payload=[], context_tags=[])  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            OrganRequest(payload={}, context_tags=["valid", 1])  # type: ignore[list-item]

    def test_response_validates_success_and_error_fields(self) -> None:
        with self.assertRaises(ValueError):
            OrganResponse(success=False, data={})
        with self.assertRaises(ValueError):
            OrganResponse(success=True, data={}, error="unexpected")


class OrganRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.organs_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def add_organ(self, name: str, engine: str) -> None:
        organ_dir = self.organs_dir / name
        organ_dir.mkdir()
        (organ_dir / "__init__.py").write_text("", encoding="utf-8")
        (organ_dir / "contract.py").write_text(
            "from orchestrator.organ_contract import OrganRequest, OrganResponse\n",
            encoding="utf-8",
        )
        (organ_dir / "engine.py").write_text(engine, encoding="utf-8")

    def test_discovers_and_executes_organ_using_shared_contract(self) -> None:
        self.add_organ(
            "EchoOrgan",
            "from .contract import OrganResponse\n"
            "def execute(request):\n"
            "    return OrganResponse(success=True, data=request.payload)\n",
        )

        registry = OrganRegistry(self.organs_dir)
        registered = registry.discover()
        response = registry.execute(
            "EchoOrgan", OrganRequest(payload={"message": "hello"}, context_tags=["test"])
        )

        self.assertEqual(set(registered), {"EchoOrgan"})
        self.assertEqual(response.data, {"message": "hello"})

    def test_skips_empty_placeholder_engines(self) -> None:
        self.add_organ("Placeholder", "")

        registry = OrganRegistry(self.organs_dir)

        self.assertEqual(dict(registry.discover()), {})

    def test_rejects_nonempty_engine_without_execute(self) -> None:
        self.add_organ("InvalidOrgan", "VALUE = 1\n")

        with self.assertRaisesRegex(OrganLoadError, "execute"):
            OrganRegistry(self.organs_dir).discover()

    def test_reports_missing_organs_directory(self) -> None:
        missing = self.organs_dir / "missing"

        with self.assertRaises(NotADirectoryError):
            discover_organs(missing)

    def test_rejects_handler_returning_wrong_type(self) -> None:
        self.add_organ("InvalidResponse", "def execute(request):\n    return {}\n")
        registry = OrganRegistry(self.organs_dir)
        registry.discover()

        with self.assertRaisesRegex(TypeError, "expected OrganResponse"):
            registry.execute("InvalidResponse", OrganRequest(payload={}))

    def test_discovers_and_executes_ingestion_pipeline(self) -> None:
        registry = discover_organs()
        self.assertIn("IngestionPipeline", registry.handlers)

        single = registry.execute(
            "IngestionPipeline",
            OrganRequest(payload={"source": "example"}, context_tags=["demo"]),
        )
        batch = registry.execute(
            "IngestionPipeline",
            OrganRequest(payload={"records": [{"id": 1}, {"id": 2}]}),
        )

        self.assertTrue(single.success)
        self.assertEqual(
            single.data,
            {
                "records": [{"source": "example"}],
                "record_count": 1,
                "context_tags": ["demo"],
            },
        )
        self.assertTrue(batch.success)
        self.assertEqual(batch.data["record_count"], 2)

    def test_ingestion_pipeline_rejects_malformed_records(self) -> None:
        registry = discover_organs()
        response = registry.execute(
            "IngestionPipeline",
            OrganRequest(payload={"records": [{"id": 1}, "invalid"]}),
        )

        self.assertFalse(response.success)
        self.assertIn("records[1]", response.error or "")


if __name__ == "__main__":
    unittest.main()
