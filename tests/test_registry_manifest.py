import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


class RegistryManifestTests(unittest.TestCase):
    def test_root_registry_matches_manifest_schema(self) -> None:
        schema = json.loads(
            (ROOT / "renzoverse_spine/registry_manifest/schema.json").read_text(
                encoding="utf-8"
            )
        )
        manifest = json.loads(
            (ROOT / "renzoverse.json").read_text(encoding="utf-8")
        )

        errors = list(Draft202012Validator(schema).iter_errors(manifest))

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()