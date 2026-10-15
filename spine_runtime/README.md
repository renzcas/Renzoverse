# Spine Runtime

`spine_runtime` is a small parent-repository runtime for loading the checked-in Spine schemas, validating messages, routing validated messages to in-process handlers, and exercising deterministic fixture flows. It has no dependency on CaveSharp and does not modify the viewer or existing Python organ registry.

## Install and run

From the repository root:

```sh
python3 -m pip install -r spine_runtime/requirements.txt
python3 -m unittest discover -s spine_runtime/harness -p '*.py' -v
```

The validator uses the `jsonschema` library for complete JSON Schema Draft 2020-12 behavior. No schemas are downloaded at runtime; the runtime only loads the checked-in local schemas and rejects remote `$ref` dependencies.

## API

```python
from spine_runtime.contract_router import ContractRouter
from spine_runtime.contract_validator import ContractValidator
from spine_runtime.mock_bus import MockBus

validator = ContractValidator()
router = ContractRouter(validator)
received = []
router.register("telemetry_contract", "viewer-fixture", received.append)

bus = MockBus()
bus.publish_all(router)
```

The router validates before dispatch. An invalid message, unknown contract, missing route, or failing handler raises an explicit runtime error; it is never silently converted to a success-shaped result. Handlers are synchronous and in-process. This is not a network broker or a command authorization service.

`MockBus` reads deterministic local files:

- `mock_bus/telemetry_stream.json`: telemetry snapshot list
- `mock_bus/world_state.json`: one world definition
- `mock_bus/event_stream.json`: event list
- `mock_bus/module_stream.json`: module manifest list

The mock module catalog validates module manifests and known contract-version references, but does not import or execute those modules. The existing `orchestrator.OrganRegistry` remains a separate local Python execution registry.

## Harness scope and limitations

The harness validates fixture shapes, routing, a documented legacy-telemetry conversion, and viewer-facing field availability. It does **not** run a browser, assert actual DOM rendering, change the viewer, exercise the existing organ execution registry with network messages, or verify CaveSharp/runtime integration. Those remain separate activation gates.

The telemetry adapter requires the caller to supply an authoritative world ID, simulation tick, timestamp, and stable creature-ID mapping. It refuses to invent them. Its output is contract-validated before it is returned.

At the creature boundary, it accepts the pinned `System.Text.Json` PascalCase DTO properties and the local camelCase serializer shape, normalizing both to the contract's camelCase fields. If both casings for a field are present, it rejects the ambiguous input.

The CaveSharp submodule also contains an opt-in C# contract snapshot builder/emitter. It requires the caller to provide authoritative envelope metadata, a stable-ID resolver, and a contract transport; it does not alter or replace the existing legacy broadcast. See the [CaveSharp shadow report](../cavesharp_shadow/delta_report.md) for the current activation boundary.
