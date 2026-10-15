"""Validate module manifests without changing the in-process organ registry."""

from unittest import TestCase

from spine_runtime.contract_errors import ContractValidationError
from spine_runtime.contract_validator import ContractValidator
from spine_runtime.mock_bus import MockBus
from spine_runtime.module_catalog import ModuleCatalog
from orchestrator.registry import discover_organs


class RegistryActivationTests(TestCase):
    def test_module_stream_loads_as_manifest_catalog(self) -> None:
        validator = ContractValidator()
        manifests = MockBus(validator).read_channel("module_stream")
        catalog = ModuleCatalog(validator).load(manifests)

        self.assertEqual(
            set(catalog),
            {"renzoverse.mock.viewer", "cavesharp.mock"},
        )
        self.assertIn("telemetry.consume", catalog["renzoverse.mock.viewer"]["capabilities"])

    def test_manifest_catalog_rejects_unsupported_contract_references(self) -> None:
        validator = ContractValidator()
        manifest = {
            "schemaVersion": "1.0.0",
            "moduleId": "fixture.bad",
            "displayName": "Bad Fixture",
            "version": "0.1.0",
            "source": {"repository": "local-fixture"},
            "capabilities": [],
            "contracts": ["urn:unknown:contract:v1@1.0.0"],
        }

        with self.assertRaisesRegex(ContractValidationError, "unsupported contract"):
            ModuleCatalog(validator).load([manifest])

    def test_existing_organ_registry_still_discovers_no_placeholders(self) -> None:
        self.assertEqual(dict(discover_organs().discover()), {})
