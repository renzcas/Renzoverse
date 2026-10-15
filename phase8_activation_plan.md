# Phase 8 — CaveSharp contract activation plan

**Phase 8 status:** planning only. No runtime wiring, configuration, transport, viewer, or Hacker-Lab changes were made during this phase. Phase 9 implementation is documented separately in the [Phase 9 report](./phase9_contract_transport.md).

Phase 7 added an opt-in builder and emitter, but the running Overseer still publishes only its legacy WebSocket payload. Phase 8 defines the proposed sources, boundary, and gates for a later activation. The recommendations below are not evidence that those sources or services already exist.

## Proposed authoritative metadata sources

| Value | Proposed owner/source | Current evidence | Activation condition |
|---|---|---|---|
| `worldId` | Renzoverse-authored `world_contract` catalog; CaveSharp receives the selected stable ID through explicit configuration. Configuration references an ID; it does not create or derive one. | No canonical world catalog or CaveSharp world ID is currently wired. `renzoverse.json` is module configuration, not a world definition. | An authored world entry exists, validates against `world_contract`, and the configured ID resolves to exactly one entry. Missing or unknown IDs stop v1 publication. |
| `tick` | The simulation update-loop owner, incremented once per completed world-state update and passed to the Overseer with the captured state. | `UpdateLoop` has a local loop counter, but it is not supplied to `Overseer`; it is scoped to `Start()` and is not established as a durable world tick. | Define restart/persistence semantics and expose one authoritative, non-negative tick that corresponds to the snapshot state. Do not substitute wall-clock time or publication count. |
| `generatedAt` | UTC wall-clock timestamp captured once at the snapshot boundary with `DateTimeOffset.UtcNow`, then passed to the builder. | The update loop logs `DateTime.UtcNow`, but that log value is not an authoritative snapshot timestamp. | Capture the time with the snapshot and serialize it as RFC 3339 UTC. Do not recalculate it during serialization or transport retries. |
| Creature `entityId` | Stable instance identity assigned by the world/creature registry at registration or spawn, and retained for that creature's lifetime (and across persistence/reload if entities survive restart). The resolver must map each source creature to that assigned ID. | `CreatureSnapshot` contains no instance ID; current `CreatureManager.GetSnapshot()` copies display data only. Names, positions, and list indices are not unique identities. | Add or expose an identity-preserving capture path before activation. Resolver results must be non-empty and unique per snapshot. Never infer IDs from names, coordinates, or array order. |
| Corruption grid | Existing source `float[,]` copied without transposition into JSON rows: outer array is source dimension 0, inner array is source dimension 1. | The builder supports this shape conversion. Axis meaning, origin, coordinate mapping, and units are not documented. | Snapshot publication may preserve the raw axes, but any spatial interpretation, overlay, or heatmap remains blocked until grid semantics are authored and tested. |

The builder's ID resolver currently receives a detached `CreatureSnapshot`, which itself has no identity provenance. Do not implement a name-based resolver to satisfy it. Before runtime activation, provide an identity-preserving snapshot/lookup route (for example, capture source creatures and their IDs together under the simulation owner) and test consistency if creatures can be registered or removed during capture.

## Overseer activation boundary

The proposed integration point is after the simulation update has completed and the Overseer has collected the telemetry values for that same state. The Overseer should call the contract emitter only when all of the following are true:

1. An explicit `contractTelemetryEnabled` opt-in is true; default is false.
2. The configured world ID resolves to the selected authored world.
3. The tick belongs to the captured world state and follows the agreed restart policy.
4. A captured UTC timestamp and complete stable creature identities are available.
5. The snapshot builder succeeds and the complete serialized output passes the checked-in `telemetry_contract` validator.
6. The separate contract transport is ready.

If any precondition fails, do not publish a partial or default-filled v1 frame. Keep legacy behavior unchanged and report an explicit contract-channel error through the repository's normal logging/health mechanism. A contract transport failure must not be represented as a successful publish; retry/backpressure policy must be bounded and must not stall simulation updates indefinitely.

The contract path is additive and isolated. Do not replace the legacy payload, change its casing, send v1 frames to existing legacy clients, or modify viewer/Hacker-Lab behavior as part of Phase 8.

## Proposed first transport: separate latest-snapshot file

For the first local activation, use a separate file snapshot rather than multiplexing contract JSON onto the legacy WebSocket:

- Proposed path: `shared/telemetry/cavesharp.v1.json`, configured separately from the reserved `telemetry_out` legacy path.
- Wire shape: one complete `telemetry_contract` JSON object per file; no line framing, event history, or command channel.
- Publish operation: serialize and validate first, write a uniquely named temporary file in the destination directory, then atomically replace/move it to the configured destination. Never truncate the live file before the new snapshot is complete.
- Reader behavior: consumers may poll/read the latest complete snapshot. File replacement is not a durable queue and does not guarantee that every intermediate tick is observed.
- Lifecycle: create/verify the configured directory at startup only when the opt-in is enabled; surface permission, path, validation, and write failures explicitly; cancel pending work and clean up owned temporary files on shutdown.
- Compatibility: use a distinct path so existing consumers and the legacy socket are unaffected. Do not reuse `shared/telemetry/cavesharp.json` until its contract and consumers are verified.

This is a proposed transport for local snapshot exchange, not a decision that the file can be served to browsers or that it satisfies remote, durable, replay, or multi-writer requirements. Revisit transport choice before any remote or multi-consumer production deployment.

## Activation gates

### Gate A — Source and identity readiness

- Pinned source/build status is recorded separately from existing local submodule edits.
- A valid authored world definition exists and the configured `worldId` resolves to it.
- Tick ownership, increment point, and process-restart semantics are documented and tested.
- Creature registration/spawn provides stable instance IDs, and telemetry capture preserves the relationship between each source creature and its ID.
- Timestamp capture happens once for the same snapshot.
- Grid axis preservation is tested; spatial semantics remain explicitly unknown until authored.

### Gate B — Contract output and transport

- Harness cases validate complete output against the canonical v1 JSON Schema, not only selected JSON keys.
- Cases cover absent/duplicate IDs, missing/invalid metadata, negative tick, non-finite values, jagged/empty grids, serialization failure, and transport failure.
- Invalid snapshots are never published; successful writes are complete atomic replacements at the separate v1 path.
- Legacy output bytes/shape and current WebSocket clients remain unaffected.

### Gate C — Runtime opt-in

- A configuration flag is explicitly enabled in a controlled local environment; default remains disabled.
- An integration test observes a v1 file and a legacy frame from the same simulation update, with matching world/tick and valid timestamp/identity data.
- Startup, write failure, cancellation, and shutdown behavior are exercised.
- The existing engine build limitations are resolved or accurately isolated in a reproducible harness.

### Gate D — Consumer activation

- **Viewer:** remains on the legacy stream until a separately approved client change can access the v1 transport. Before switching, validate valid/invalid fixtures, stale/error presentation, and matching `worldId`; do not infer grid geometry.
- **Hacker-Lab:** do not claim activation until its source repository is available and its actual consumers are mapped. Then use the canonical schema and fixtures, read-only telemetry access by default, and explicit handling for stale or invalid snapshots.
- Neither consumer gate is implied by an engine harness pass or by writing a local snapshot file.

## Current disposition

Phase 8 defined a recommended metadata ownership model, opt-in boundary, and first transport proposal. It did **not** activate CaveSharp during that phase. The follow-on transport, metadata sources, and opt-in Overseer wiring are implemented in Phase 9; the full engine's runtime and consumer access remain separate gates.
