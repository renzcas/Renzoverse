# Contract activation plan

This plan activates contracts at the two local boundaries that can be exercised without modifying CaveSharp runtime code: the Renzos-Cave browser client/test mock and the local Python organ registry. “Activation” means validation and explicit metadata, not that the external pillars are already integrated.

## Contract boundaries to preserve

- `telemetry_contract` is the current snapshot contract; it contains creature and corruption fields. There is no standalone `snapshot_contract`, `creature_contract`, or `corruption_contract` in v1.
- `world_contract` describes stable authored worlds/regions/entity types. Runtime browser keyboard/pointer events are not `event_contract` world events.
- `event_contract` is for ordered simulation/domain events. Viewer controls should not use it unless a deliberate client-command/event protocol is designed.
- `command_contract` is for explicit authorized commands to a runtime, not generic in-process Python function invocation. The existing `OrganRequest`/`OrganResponse` stays a local Python contract.
- `module_contract` describes a module. Placeholder organs need metadata to be listed, but they do not consume command/event contracts until real behavior requires those interfaces.

## Workstream A — Viewer and mock telemetry

### A1. Add shared fixtures and consumer validation

- Create valid and invalid telemetry/world fixture documents derived from the canonical JSON Schemas.
- Select one maintained validation strategy for the plain browser client (for example, generated validator artifacts or a small runtime validator tested against schema fixtures); do not install a dependency or duplicate schema until the project setup is inspected.
- Validate `schemaVersion`, required envelope values, finite numeric fields, and every creature item before mutating HUD state.
- On invalid input, preserve/mark the last valid state as stale or show unavailable; never coerce missing required values to zero or update connection status to live-valid.
- Keep transport errors, JSON parse errors, schema errors, and unsupported versions distinguishable.

**Acceptance:** valid v1 fixture updates the HUD; missing `worldId`, unsupported version, invalid creature fields, non-finite values, and malformed JSON are rejected without presenting a successful fresh snapshot.

### A2. Add an explicit mock mode

- Update or extend `tests/mock_cavesharp_telemetry.py` to serve a valid v1 fixture from a shared fixture file.
- If legacy payload testing is still needed, label it explicitly as legacy and keep it separate from v1 mode.
- Keep mock output deterministic and test its payload with the same canonical schema validator used for fixture validation.

**Acceptance:** the browser connects to the v1 mock and renders a valid sample; invalid fixture mode demonstrates visible client validation errors. Existing legacy tests remain clearly marked.

### A3. World catalog and overlays

- Add a minimal world fixture satisfying `world_contract` with stable world/region/entity-type IDs.
- Decide whether the viewer scene/overlays are data-driven before wiring in catalog fetches.
- Region overlays resolve stable region definitions from the world document and dynamic values from telemetry; no ad-hoc region names or assumed grid coordinates.
- Defer corruption heatmap rendering until `corruptionGrid` units, orientation, origin, and mapping to regions are agreed.

**Acceptance:** fixture world validates and any implemented overlay references known region IDs; absent or mismatched world IDs are reported rather than guessed.

### A4. Viewer controls and input boundary

- Keep WASD, pointer-lock, and local camera movement as presentation/input behavior.
- If controls later mutate simulation state, design a separate command client using `command_contract`, with authorization and engine-side validation.
- Do not encode browser keypresses as `event_contract` domain events without a specific event-stream use case.

**Acceptance:** local controls remain functional without a simulation event stream; any future world-mutating control requires command result/error handling.

## Workstream B — Python organ registry and module manifests

### B1. Validate module manifests

- Add explicit manifest metadata for real executable organs and validate it with `module_contract/schema.json` during discovery.
- Keep inventory-only placeholder entries clearly marked non-executable; do not require placeholder engines to fabricate command/event capabilities.
- Test missing/invalid manifest, duplicate module ID, unsupported contract version, empty engine, and valid executable module cases.
- Preserve the existing Python `OrganRequest`/`OrganResponse` API for in-process execution.

**Acceptance:** registry reports discovered modules with stable IDs and declared contracts; invalid manifests fail explicitly; no placeholder is presented as executable.

### B2. Keep commands and events separate from local invocation

- Do not route generic `registry.execute(name, OrganRequest(...))` through `command_contract`.
- Add a command adapter only for an explicit remote/authorized operation that acts on simulation state, with actor identity, world ID, validation, audit, and result message.
- Add an event publisher/consumer only for organs whose specified behavior actually emits or consumes domain events; require event-type payload schemas and sequence semantics.

**Acceptance:** local organ tests continue to exercise the in-process API; any newly added wire command/event has schema fixtures and explicit authorization/order tests.

### B3. Telemetry and dashboards

- The current local registry does not consume snapshots. Add a telemetry adapter only if an organ has a specified snapshot-driven capability.
- Hacker-Lab dashboards remain unverified until that repository is available. When available, make dashboards read validated telemetry/event/module contracts rather than giving the Python registry implicit dashboard responsibilities.

**Acceptance:** no telemetry or dashboard capability is advertised by a module until it has a concrete implementation and conformance test.

## Sequence and gates

1. **Fixture gate:** schemas validate all shared fixtures; fixture contract/version references are explicit.
2. **Viewer gate:** browser validates v1 telemetry and reports invalid/stale data correctly against the mock.
3. **World gate:** world fixture and optional overlays use stable IDs and documented geometry.
4. **Registry gate:** Python discovery validates module manifests without breaking existing local execution semantics.
5. **External-client gate:** only after Hacker-Lab source is available, map its actual consumers/producers and run the same fixtures.
6. **CaveSharp gate:** the local-only Phase 7 builder/emitter and Phase 8 activation proposal are documented separately in the [CaveSharp delta report](./cavesharp_shadow/delta_report.md) and [Phase 8 activation plan](./phase8_activation_plan.md). Do not mark CaveSharp adapter-conformant or runtime-conformant until authoritative metadata/identity, schema validation, a separate transport, and the activation tests pass.

This plan does not wire or activate CaveSharp runtime behavior. Do not claim a pillar is contract-activated based only on schema validity or a mock connection.
