import importlib.util
import json
import logging
import sys
import uuid
from collections.abc import Callable, Mapping
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Any

from orchestrator.organ_contract import OrganRequest, OrganResponse
from spine_runtime.contract_validator import ContractValidator
from spine_runtime.module_catalog import ModuleCatalog


LOGGER = logging.getLogger(__name__)
DEFAULT_ORGANS_DIR = (
    Path(__file__).resolve().parents[1] / "master_core" / "UTL" / "organs"
)
OrganHandler = Callable[[OrganRequest], OrganResponse]
MANIFEST_FILENAME = "manifest.json"


class OrganLoadError(RuntimeError):
    """An organ module exists but does not satisfy the loadable-organ contract."""


class OrganRegistry:
    def __init__(self, organs_dir: str | Path = DEFAULT_ORGANS_DIR) -> None:
        self.organs_dir = Path(organs_dir).resolve()
        self._handlers: dict[str, OrganHandler] = {}
        self._manifests: dict[str, Mapping[str, Any]] = {}
        self._module_namespace = f"_renzoverse_organs_{uuid.uuid4().hex}"

    @property
    def handlers(self) -> Mapping[str, OrganHandler]:
        return self._handlers.copy()

    @property
    def manifests(self) -> Mapping[str, Mapping[str, Any]]:
        return self._manifests.copy()

    def discover(self) -> Mapping[str, OrganHandler]:
        if not self.organs_dir.is_dir():
            raise NotADirectoryError(f"Organ directory not found: {self.organs_dir}")

        namespace = ModuleType(self._module_namespace)
        namespace.__path__ = [str(self.organs_dir)]
        namespace.__package__ = self._module_namespace
        namespace.__spec__ = ModuleSpec(
            self._module_namespace, loader=None, is_package=True
        )
        namespace.__spec__.submodule_search_locations = [str(self.organs_dir)]
        sys.modules[self._module_namespace] = namespace

        candidates: list[tuple[str, Path, Path, Mapping[str, Any]]] = []
        for organ_dir in sorted(self.organs_dir.iterdir(), key=lambda path: path.name.casefold()):
            if not organ_dir.is_dir() or organ_dir.name.startswith("."):
                continue

            engine_path = organ_dir / "engine.py"
            if not engine_path.is_file():
                continue
            if not engine_path.read_text(encoding="utf-8").strip():
                LOGGER.info("Skipping empty organ placeholder: %s", organ_dir.name)
                continue
            if not organ_dir.name.isidentifier():
                raise OrganLoadError(
                    f"Organ directory name must be a Python identifier: {organ_dir}"
                )

            try:
                manifest_path = organ_dir / MANIFEST_FILENAME
                if not manifest_path.is_file():
                    raise FileNotFoundError(
                        f"Required organ manifest not found: {manifest_path}"
                    )
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if not isinstance(manifest, dict):
                    raise TypeError("manifest.json must contain a JSON object.")
            except Exception as exc:
                raise OrganLoadError(
                    f"Could not load manifest for organ '{organ_dir.name}': {exc}"
                ) from exc

            candidates.append((organ_dir.name, organ_dir, engine_path, manifest))

        try:
            manifest_catalog = ModuleCatalog(ContractValidator()).load(
                [manifest for _, _, _, manifest in candidates]
            )
        except Exception as exc:
            raise OrganLoadError(f"Invalid organ manifest catalog: {exc}") from exc

        discovered: dict[str, OrganHandler] = {}
        discovered_manifests: dict[str, Mapping[str, Any]] = {}
        for organ_name, organ_dir, engine_path, manifest in candidates:
            try:
                handler = self._load_handler(organ_dir, engine_path)
            except Exception as exc:
                raise OrganLoadError(
                    f"Could not load organ '{organ_name}': {exc}"
                ) from exc

            discovered[organ_name] = handler
            discovered_manifests[organ_name] = manifest_catalog[manifest["moduleId"]]

        self._handlers = discovered
        self._manifests = discovered_manifests
        LOGGER.info("Discovered %d executable organ(s).", len(discovered))
        return self.handlers

    def execute(self, name: str, request: OrganRequest) -> OrganResponse:
        if not isinstance(request, OrganRequest):
            raise TypeError("request must be an OrganRequest.")
        try:
            handler = self._handlers[name]
        except KeyError as exc:
            raise KeyError(f"Organ is not registered: {name}") from exc

        try:
            response = handler(request)
        except Exception as exc:
            raise RuntimeError(f"Organ '{name}' failed during execution: {exc}") from exc
        if not isinstance(response, OrganResponse):
            raise TypeError(
                f"Organ '{name}' returned {type(response).__name__}; "
                "expected OrganResponse."
            )
        return response

    def _load_handler(self, organ_dir: Path, engine_path: Path) -> OrganHandler:
        package_name = f"{self._module_namespace}.{organ_dir.name}"
        package_spec = importlib.util.spec_from_file_location(
            package_name,
            organ_dir / "__init__.py",
            submodule_search_locations=[str(organ_dir)],
        )
        if package_spec is None or package_spec.loader is None:
            raise ImportError(f"Could not create package loader for {organ_dir}")

        package = importlib.util.module_from_spec(package_spec)
        sys.modules[package_name] = package
        package_spec.loader.exec_module(package)

        engine_name = f"{package_name}.engine"
        engine_spec = importlib.util.spec_from_file_location(engine_name, engine_path)
        if engine_spec is None or engine_spec.loader is None:
            raise ImportError(f"Could not create engine loader for {engine_path}")

        engine = importlib.util.module_from_spec(engine_spec)
        sys.modules[engine_name] = engine
        engine_spec.loader.exec_module(engine)

        handler: Any = getattr(engine, "execute", None)
        if not callable(handler):
            raise TypeError("engine.py must define a callable execute(request) handler.")
        return handler


def discover_organs(organs_dir: str | Path = DEFAULT_ORGANS_DIR) -> OrganRegistry:
    """Discover executable organs in the configured organs directory."""
    registry = OrganRegistry(organs_dir)
    registry.discover()
    return registry
