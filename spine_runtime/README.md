# Spine Runtime

`spine_runtime` is a small parent-repository runtime for loading the checked-in Spine schemas, validating messages, routing validated messages to in-process handlers, exercising deterministic fixture flows, and serving read-only viewer and module-status APIs. It has no dependency on CaveSharp and does not modify the existing Python organ registry.

## Install and run

From the repository root:

```sh
python3 -m pip install -r spine_runtime/requirements.txt
python3 -m unittest discover -s spine_runtime/harness -p '*.py' -v
```

The validator uses the `jsonschema` library for complete JSON Schema Draft 2020-12 behavior. No schemas are downloaded at runtime; the runtime only loads the checked-in local schemas and rejects remote `$ref` dependencies.

## Live CaveSharp telemetry

Install the requirements, then start the processes in separate terminals from the repository root:

```sh
DOTNET_ROLL_FORWARD=Major dotnet run --no-build --project modules/CaveSharp-OS/CaveSharpEngine.csproj -- --legacy --ticks 0
python3 -m spine_runtime.telemetry_bridge --world-id renzoverse.cavesharp.primary
python3 -m spine_runtime.viewer_server --host 0.0.0.0 --port 8000
```

`--ticks 0` keeps the legacy simulation running until it is stopped with Ctrl+C; omitting it keeps the existing 100-tick smoke-test behavior. The bridge reconnects to `ws://localhost:8181/telemetry/`, validates each converted packet against the checked-in [telemetry schema](../renzoverse_spine/telemetry_contract/schema.json), and atomically replaces `shared/telemetry/cavesharp.v1.json`. The viewer reads that latest snapshot from `/api/telemetry/v1/latest`. In Codespaces, forward port 8000 to open the viewer.

The v1 snapshot envelope includes `schemaVersion`, authored `worldId`, increasing `tick`, UTC `generatedAt`, threat/CTA/corruption values, and the complete creature and corruption-grid state. Each creature must include its runtime `entityId`; the bridge rejects packets without it rather than fabricating identity. `weather` is preserved as an allowed extension field.

Example snapshot shape:

```json
{
	"schemaVersion": "1.0.0",
	"worldId": "renzoverse.cavesharp.primary",
	"tick": 42,
	"generatedAt": "2026-11-05T10:30:00+00:00",
	"threat": 24,
	"cta": 18,
	"corruption": 12.5,
	"weather": "Storm",
	"ctaBoss": "Overlord-Alpha",
	"directive": "Monitor corruption nodes",
	"creatures": [
		{
			"entityId": "dacbcbada85e4ff7a05efb894d8cd638",
			"name": "TunnelRat",
			"health": 85,
			"aggression": 20,
			"hunger": 35,
			"x": -8,
			"y": 4,
			"corruptionExposure": 3,
			"isAfraid": false
		}
	],
	"corruptionGrid": [[0, 0.5], [0.25, 0]]
}
```

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

The viewer server exposes `GET /api/modules` and `GET /api/modules/{id}/status` from the root `renzoverse.json` registry. Status checks repository and entry-point presence, prerequisite executable presence, and declared telemetry-file validity. Prerequisite versions are not executed or verified; process state reports `not_managed` until a control-plane launcher owns process tracking. These routes are read-only and do not launch modules.

At the creature boundary, it accepts the pinned `System.Text.Json` PascalCase DTO properties and the local camelCase serializer shape, normalizing both to the contract's camelCase fields. If both casings for a field are present, it rejects the ambiguous input.

The CaveSharp submodule also contains an opt-in C# contract snapshot builder/emitter. It requires the caller to provide authoritative envelope metadata, a stable-ID resolver, and a contract transport; it does not alter or replace the existing legacy broadcast. See the [CaveSharp shadow report](../cavesharp_shadow/delta_report.md) for the current activation boundary.
