# Contract flow simulation

This is a design-time simulation of intended message flow. It is not runtime wiring. “Current” describes evidence in this checkout; “target” describes a future flow after adapters, contract tests, and owners are in place.

## 1. Engine → telemetry snapshot → viewer

```text
CaveSharp simulation state
    └─ snapshot adapter (not v1-conformant yet)
         └─ telemetry_contract v1 complete snapshot
              └─ WebSocket or other chosen transport
                   └─ viewer validates schema/version
                        └─ HUD + creature markers + derived displays
```

### Example snapshot content

| Display/data | Contract field | Current local evidence | Target handling |
|---|---|---|---|
| Creature snapshot | `creatures[]` | Local serializer/harness and legacy mock include creature arrays; creature DTO currently lacks an emitted stable ID, and manager does not populate corruption exposure | Validate every required item; use stable `entityId`, never display name or array index as durable identity |
| Corruption snapshot | `corruption`, `corruptionGrid` | Scalar and grid exist in the local serializer design; viewer reads scalar but does not render grid | Keep scalar/grid as telemetry; document units, axes, origin, and grid dimensions before visualization |
| Region snapshot/context | `worldId` plus matching world catalog `regions[]` | Runtime `RealmRegion` and map classes exist; no canonical catalog or region overlay consumer found | Resolve stable region IDs and geometry through `world_contract`; do not embed unstable display names as IDs |
| CTA snapshot | `cta`, `ctaBoss`, `directive` | Legacy payload/serializer contains these fields | Keep values in telemetry; specify units and ranges and validate before display |
| Snapshot envelope | `schemaVersion`, `worldId`, `tick`, `generatedAt` | Missing from the inspected legacy payload | Populate from authoritative catalog/runtime clock; never fabricate metadata in viewer or serializer |

**Failure simulation:** if JSON is malformed, the schema version is unsupported, or a required field is missing, the viewer reports invalid/stale data and does not convert the field to zero or claim that a valid fresh snapshot arrived. A dropped connection is a transport state, not a schema error. A gap in a snapshot stream is recovered by requesting/reconnecting to a fresh complete snapshot; events are not required for viewer rendering.

## 2. World catalog → engine and viewer

```text
Renzoverse authored world catalog
    └─ world_contract v1
         ├─ CaveSharp: configuration/identity inputs (when adopted)
         └─ Renzos-Cave: world/region/entity definitions (when scene is data-driven)
```

The catalog describes stable authored identity and definitions; it is not a copy of each simulation tick.

| Example | `world_contract` role | Runtime role |
|---|---|---|
| Region definition/ID | Authored stable region entry | Engine state refers to region ID; viewer may render its overlay |
| Creature type | Authored entity type | Snapshot creature instance has stable entity ID and current values |
| Corruption rules | Authored configuration only if owners define them as world content | Current corruption value/grid remains telemetry; transitions may become events |
| Geometry/map | Stable region/world geometry if included in catalog | Camera-local coordinates and transient movement are not world-definition messages |

Unknown world IDs or region references are explicit compatibility errors. Clients must not infer catalog membership from `RealmRegion.Name` or coordinates.

## 3. Viewer → command → engine

```text
Viewer UI action
    ├─ camera movement / pointer lock / creature focus / region selection
    │    └─ local presentation state; no Spine message
    └─ explicit simulation-changing action (future only)
         └─ authorized command client
              └─ command_contract request
                   └─ CaveSharp validates + authorizes + audits
                        └─ command_contract result
```

| Interaction | Contract flow |
|---|---|
| Scene movement, camera look, creature focus, region selection | Local UI behavior; no `event_contract` or `command_contract` needed |
| Requesting an engine-side CTA change | Future typed `command_contract` request, if supported and authorized; explicit accepted/rejected/completed result |
| Requesting a region/world mutation | Future command only if product behavior requires it and the engine defines the operation |

Commands require authenticated actor identity, allow-listed types, payload validation, idempotency/audit policy, and a correlated result. No such viewer command client is established in this checkout. Never translate a browser keypress directly into an engine command by default.

## 4. Engine → events → cockpit

```text
Actual domain transition
    └─ event adapter + per-world sequencer
         └─ event_contract v1
              └─ cockpit/analysis consumer (external source unverified)
```

| Scenario | Event intent | Snapshot relationship |
|---|---|---|
| Corruption spike | A typed corruption threshold/transition event, only after a threshold and payload schema are defined | Snapshot still provides current corruption state; event indicates a transition |
| CTA trigger | A typed CTA event from the actual trigger/transition point | Snapshot reflects current CTA/boss/directive after the transition |
| Creature state change | Emit only selected meaningful lifecycle/state transitions, not every field update unless throughput/replay needs justify it | Snapshot remains the recovery/current-state source |

Every event needs an event ID, world ID, monotonic per-world sequence, authoritative tick, timestamp, type, and type-specific payload. Existing CTA/time/interaction event-related classes have not been shown to publish a unified stream. Consumers detect sequence gaps and recover from a fresh snapshot; they must not assume WebSocket telemetry is an event log.

## 5. Cockpit → module catalog → engine

```text
Renzoverse module catalog
    └─ module_contract manifests
         └─ cockpit module/health panels (future; repo unverified)

Cockpit operator action
    └─ authenticated command_contract request
         └─ target module validates capability + command
              └─ command_contract result
```

| Proposed action | Required contract | Guardrail |
|---|---|---|
| Show module identity, version, capabilities, compatible contract versions | `module_contract` | A manifest is descriptive metadata, not proof that a module is healthy or running |
| Display world state | `telemetry_contract`; `world_contract` for labels/regions | Validate schema and show snapshot age/tick |
| Show transitions/alerts | `event_contract` | Require event sequence and replay/gap policy |
| Request agent/CTA/symbolic action | `command_contract` only if the target module explicitly exposes an authorized operation | Do not infer operation names from module names or agent dashboards |
| “Module transform” | Module-specific capability and payload definition; possibly event output or command input | No generic transform message exists in v1; define a typed contract before integration |

The local `OrganRegistry` is not this cockpit. It imports local Python engines and uses `OrganRequest`/`OrganResponse`; current organ engines are placeholders. A remote module invocation or dashboard connection requires a deliberate service boundary and manifest, not just schema attachment.

## End-to-end recovery paths

- **Snapshot client:** on connect, obtain a complete valid telemetry snapshot; on invalid message, surface a validation error; on reconnect, acquire a fresh snapshot and mark any retained prior values stale.
- **Event client:** persist/track per-world sequence; on gap, request/reacquire a snapshot and resume from an explicit cursor if event replay is implemented.
- **Command client:** send one authorized request with a unique command ID; handle accepted/rejected/completed result and timeout without retrying non-idempotent actions blindly.
- **Module client:** load a validated manifest; discover health separately; do not treat a manifest's advertised capability as an executed/tested capability.
