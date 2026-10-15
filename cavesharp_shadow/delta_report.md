# CaveSharp contract delta report

This report compares the **pinned CaveSharp source at `6d4efc9d2753a11b4680a4969eb6041b65d39b22`** and separately labeled local submodule edits against the draft Spine schemas. It describes source-level payload intent, not a proven successful runtime emission: the pinned creature DTO and manager have a source mismatch, and direct multidimensional-array JSON serialization is unverified.

Detailed machine-readable shadows:

- [Snapshot/root payload](./snapshot_shadow.json)
- [Creature DTO](./creature_shadow.json)
- [Corruption state](./corruption_shadow.json)
- [World/region state](./region_shadow.json)
- [Overseer producer](./overseer_shadow.json)

## Field-level telemetry delta

| Source field | Pinned source shape | Spine target | Delta | Classification |
|---|---|---|---|---|
| `threat` | Root anonymous object property; `int` from `GlobalThreatLevel` | Required `number` at `$.threat` | JSON number is compatible; unit/range semantics remain unspecified | Legacy overlap; boundary mapping needed |
| `cta` | Root property; `float` from `CTABoss.AggressionLevel` | Required `number` at `$.cta` | Type compatible; label/range/units need agreement | Legacy overlap; semantics gap |
| `corruption` | Root property; `float` from `SpreadIntensity` | Required `number` at `$.corruption` | Type compatible; implementation clamps at 100, but percentage semantics are not established | Legacy overlap; semantics gap |
| `ctaBoss` | Root property; `string` from boss name | Required `string` | Shape overlaps; not a stable boss ID | Legacy overlap |
| `directive` | Root property; `string` from `GetDirective()` | Required `string` | Shape overlaps; directive vocabulary/version not cataloged | Legacy overlap |
| `creatures` | Root array of `CreatureSnapshot`; default `System.Text.Json` options preserve nested PascalCase properties | Required array of objects with camel-case fields and stable `entityId` | Casing mismatch; missing stable ID; pinned DTO/manager build-time mismatch; local DTO changes are not pinned | Requires adapter and source repair |
| `creatures[].Name` / `.Health` / `.Aggression` / `.X` / `.Y` / `.CorruptionExposure` | Pinned DTO declares these PascalCase properties | `name`, `health`, `aggression`, `x`, `y`, `corruptionExposure` | Casing mismatch; JSON keys are case-sensitive to consumers | Adapter can normalize casing |
| `creatures[].Hunger` / `.IsAfraid` | Manager assigns them, but they are absent from the pinned DTO; local DTO adds them | Required `hunger` / `isAfraid` | Pinned source does not compile consistently across these files; local additions are uncommitted; manager must populate values | Build blocker / source alignment |
| `creatures[].CorruptionExposure` | DTO declares it; inspected manager does not assign it in `GetSnapshot()` | Required numeric value | Default may be emitted instead of the creature's runtime value; silently accepting it would be misleading | Source mapping required |
| `creatures[].entityId` | No stable identity in pinned or inspected local DTO | Required non-empty stable ID | No source value or mapping | Requires world/entity identity decision |
| `corruptionGrid` | Root property receives `float[,]` from `GetGrid()` | Required array of arrays of numbers | CLR multidimensional array shape is not the schema shape; built-in serializer support is unverified and may throw | Boundary conversion required |
| `schemaVersion` | Absent | Required constant `"1.0.0"` | Missing | Additive at adapter boundary |
| `worldId` | Absent | Required stable non-empty world ID | Missing and no canonical world catalog/identity is wired | World catalog alignment required |
| `tick` | Absent from payload; loop exists but authoritative shared counter is not established | Required non-negative integer | Missing | Requires tick-owner decision; do not fabricate |
| `generatedAt` | Absent | Required date-time | Missing | Can be added at snapshot boundary using UTC clock after generated-time semantics are accepted |

## World and region delta

| Source | Existing shape | `world_contract` requirement | Delta / work |
|---|---|---|---|
| `Realm/RealmRegion.cs` | Name, resonance factor, harmonic level, ambience, light shift | Stable `regionId`, name, optional description/parent/metadata within a world document | Name is not an ID; no catalog or region serialization was identified |
| `Map/MapEngine.cs`, `Systems/World/MapEngine.cs`, `Environment/World.cs` | Runtime map/world implementation types | Stable `worldId`, `worldVersion`, named regions and entity types | No canonical authored world document; overlapping source locations need ownership review |
| Overseer telemetry | No world or region fields | World catalog establishes identities; telemetry references its `worldId` | Add catalog and identity mapping before region overlays or cross-world consumption |

Region runtime state, corruption measurements, and changing harmonics should not be stuffed into static world definitions. If consumers need changing region state, define its telemetry representation and stable region references separately.

## Event and command delta

| Boundary | Existing source shape | Spine target | Gap |
|---|---|---|---|
| Event producers | CTA, time, and interaction event-related classes; no unified stream found | Event ID, world ID, per-world sequence, tick, timestamp, type, payload | Payload types, sequencing, ordering, replay, and transport are not implemented/verified |
| CTA command server/hooks | Existing handler surface and Overseer methods | Versioned request and explicit result with command/world IDs | Envelope, actor authentication, authorization, audit, idempotency, and errors are unverified |
| Viewer scene controls | Local keyboard/camera/pointer lock | No message for local-only UI actions; command only for an explicit world mutation | Do not classify selection/focus/camera actions as world commands or events by default |

## Naming, semantics, and serialization

- Root anonymous telemetry property names are lower camel case in the pinned `Overseer`; nested `CreatureSnapshot` properties remain PascalCase with default serializer options.
- The local untracked `TelemetrySnapshotSerializer` uses web JSON options, but that does not resolve missing IDs/envelope data and is not in the pinned submodule revision.
- A `float[,]` grid needs a tested conversion to JSON rows/columns. Before consumers render it, record axis order, origin, coordinate mapping, and units.
- `SpreadIntensity` is clamped in source but the contract does not define a percentage. Do not add `%` semantics or range validation without agreement.
- Do not default missing fields to zero, false, empty IDs, or current tick. Rejection is safer than success-shaped telemetry.

## Adapter disposition

### Adapter-boundary compatible (non-breaking to engine behavior)

- Add `schemaVersion`, `worldId`, `tick`, and `generatedAt` to an outer v1 envelope **only when supplied by their authoritative sources**.
- Map known numeric/string root fields and convert JSON property casing.
- Convert a supported in-memory grid representation to array-of-arrays once orientation is defined.
- Validate before publishing to a v1 channel, while preserving any legacy output route during a migration period.

### Requires source or domain decisions

- Provide stable creature IDs and a world catalog.
- Resolve the pinned `CreatureSnapshot`/`CreatureManager` compile mismatch; the adapter cannot adapt a build that cannot produce its source object.
- Populate required hunger, fear, and corruption-exposure values accurately.
- Define units/ranges for threat, CTA, corruption, and grid cells.
- Select the authoritative tick source and per-world event sequencer.
- Define typed event payloads and command type catalog, auth, audit, and result semantics.

## Blocking and non-blocking gaps

**Blocking for v1 telemetry emission:** no world ID, tick, or entity ID; pinned source mismatch for required creature fields; missing/possibly default corruption exposure; unsupported/unverified grid serialization; lack of full message validation.

**Non-blocking for a minimal snapshot:** event stream and command integration can remain disabled; viewer scene can remain static/local; region overlays can wait for a canonical world catalog. These capabilities must not be falsely advertised as active.

## Remaining activation gate

Before wiring the new components into the runtime:

1. Confirm the selected/pinned source revision and a reproducible build; keep the existing uncommitted submodule changes separate.
2. Agree on world ID, tick ownership, entity IDs, numeric semantics, and grid orientation.
3. Select a separate contract transport or prove that existing clients tolerate an additional v1 frame.
4. Validate emitted snapshots against the canonical schema, then test the opt-in runtime route without removing the legacy route.

## Phase 7 local implementation status

The submodule working tree now includes opt-in `SnapshotContractBuilder` and `ContractTelemetryEmitter` components, exercised by `tests/CaveSharpTelemetryHarness`. The builder maps legacy snapshot values to v1 fields, converts a `float[,]` corruption grid to JSON rows, and requires caller-supplied world ID, tick, timestamp, and stable creature-ID resolution. It rejects duplicate/missing IDs and non-finite numeric values. The emitter serializes the contract snapshot and publishes it only through an injected transport.

This is an adapter and harness connection, **not yet a production CaveSharp → Spine runtime connection**: the Overseer and legacy WebSocket route are unchanged, and no authoritative metadata/ID source or separate contract transport has been wired. Existing legacy consumers therefore continue receiving only their current payload. Runtime conformance remains blocked on those inputs and on the pinned source build/data gaps above.

The [Phase 8 activation plan](../phase8_activation_plan.md) records the design proposal. Phase 9 implements its local metadata sources, disabled-by-default Overseer gate, and separate latest-snapshot file transport; this does not prove a live full-engine emission or activate either consumer. See the [Phase 9 report](../phase9_contract_transport.md).
