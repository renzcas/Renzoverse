# Phase 9 — Contract transport, metadata sources, and Overseer gate

**Phase 9 status at completion:** opt-in local transport and source validation implemented. Consumer activation was intentionally deferred to Phase 10.

## Metadata sources

- **World ID:** `shared/worlds/cavesharp.json` is an authored `world_contract` document. Activation requires an explicitly configured `RENZOVERSE_CONTRACT_WORLD_ID` that exactly matches its `worldId`; the engine does not derive an ID from a name or path.
- **Tick:** `UpdateLoop` passes its completed update count to the Overseer. The current demo loop starts at tick 1 and resets on process restart. There is no persistence or cross-restart tick guarantee; any future persistent world must define that policy before using this source.
- **Generated time:** the update loop captures `DateTimeOffset.UtcNow` after the simulation update, once per snapshot, and passes it unchanged through build and publish.
- **Entity IDs:** each `Creature` receives a UUID when constructed, retained for that instance's lifetime. It is not serialized into the legacy telemetry DTO. There is no creature persistence today, so continuity across process restarts is not promised. If persistence is added, restored entities must restore their assigned IDs.
- **Creature values:** contract capture uses the same legacy telemetry snapshot as the WebSocket publish; `CorruptionExposure` is copied from the source creature instead of relying on a DTO default.

The world definition describes stable authored identities only. It does not claim that runtime creatures are assigned to regions or that corruption-grid axes have spatial meaning.

## Transport and activation gate

Contract telemetry is disabled unless `RENZOVERSE_CONTRACT_TELEMETRY_ENABLED=true`. When enabled, all of these variables are required:

```sh
RENZOVERSE_CONTRACT_TELEMETRY_ENABLED=true
RENZOVERSE_CONTRACT_WORLD_ID=renzoverse.cavesharp.primary
RENZOVERSE_WORLD_CATALOG=/absolute/path/to/shared/worlds/cavesharp.json
RENZOVERSE_CONTRACT_TELEMETRY_PATH=/absolute/path/to/shared/telemetry/cavesharp.v1.json
```

The configured world document and ID are checked before the channel activates. The contract output path cannot be the legacy `shared/telemetry/cavesharp.json`. The publisher writes one complete JSON snapshot to a unique temporary file in the destination directory, then replaces the v1 destination. At most one publish is in flight; if file I/O falls behind, later snapshots are explicitly logged and skipped rather than queuing unbounded work or blocking simulation ticks. Write/build errors are logged and never reported as successful publication.

The Overseer captures one source snapshot for both legacy and contract outputs. When Phase 9 completed, the v1 file was additive and the existing WebSocket payload bytes were unchanged; viewer consumption was switched separately in Phase 10. `CreatureSnapshot.EntityId` is ignored by JSON serialization so adding stable identities does not alter legacy wire fields.

## Verification and limitations

- The authored world document is tested against the canonical checked-in `world_contract` schema.
- The CaveSharp telemetry harness exercises explicit opt-in, metadata mismatch rejection, legacy-path protection, contract serialization, and atomic file publication.
- The C# builder validates required fields, finite numeric values, and unique non-empty entity IDs before transport. The standard Spine Python validator remains the canonical full JSON Schema validator; the running CaveSharp process does not load or execute JSON Schema itself.
- The pinned CaveSharp project has existing unrelated compile errors. This harness compiles the telemetry boundary independently and is not proof that the full engine starts or emits a live snapshot.
- Phase 9 did not activate the viewer or Hacker-Lab, nor add remote transport, a durable queue, command channel, or event stream. The follow-on consumer status is tracked in the [Phase 10 report](./phase10_viewer_activation.md).

Run the focused checks from the repository root:

```sh
dotnet run --project tests/CaveSharpTelemetryHarness/CaveSharpTelemetryHarness.csproj
python3 -m unittest spine_runtime.harness.phase9_sources_test
```

The v1 output is a latest-snapshot file, not a history or delivery guarantee. Reconsider transport before remote or multi-consumer production use.
